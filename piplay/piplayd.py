import daemon
import socket
import select
import logging
from piplay import requests, manager
from piplay.config import logging as plog

logging.basicConfig(
    level=plog.LOGLEVEL,
    format=plog.LOGFORMAT,
    filename=plog.FILENAME
)


class Server:
    """Handle incoming requests"""
    def __init__(self, address, port):
        """Constructor

        :param address: Address to bind server
        :param port: Port to bind server
        """
        self._address = address
        self._port = port
        self._socket = None
        self._daemon = None
        self._manager = None
        self.logger = logging.getLogger(__name__)

    @property
    def address(self):
        return (self._address, self._port)

    def run(self):
        """Main eventloop which handles incoming requests and send them to manager instance"""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(self.address)
        self._socket.listen(1)
        self._socket.setblocking(0)  # Non-blocking sockets
        self.logger.debug('Start listening on %s:%s', *self.address)
        epoll = select.epoll()
        epoll.register(self._socket.fileno(), select.EPOLLIN)  # We don't write back, so only reading
        try:
            EOL = b'\n\n'  # Delimiter for separate requests
            connlist = {}  # Store all incoming connections
            reqlist = {}  # Store all request data
            while True:
                events = epoll.poll(1)
                for fileno, event in events:
                    if fileno == self._socket.fileno():  # If event is on main socket then create client socket
                        self.logger.debug('New connection recieved')
                        clientconn, address = self._socket.accept()
                        clientconn.setblocking(0)
                        epoll.register(clientconn.fileno(), select.EPOLLIN)  # Only reading
                        connlist[clientconn.fileno()] = clientconn
                        reqlist[clientconn.fileno()] = b''

                    elif event and select.EPOLLIN:  # If event is on client socket then process it
                        reqlist[fileno] += connlist[fileno].recv(128)
                        # When client closes a connection from his side, he will always send
                        # EPOLLIN with "" data, so we need to process it properly
                        if not reqlist[fileno].decode():
                            self.logger.debug('Client closed a connection from his side')
                            epoll.modify(fileno, 0)
                            reqlist[fileno] = b''
                            break
                        # If it is not the end of data, process it
                        while EOL not in reqlist[fileno]:
                            # We don't want to process too long connections
                            if len(reqlist[fileno]) > 256:
                                self.logger.debug('Request is too long')
                                epoll.modify(fileno, 0)
                                reqlist[fileno] = b''
                                break

                        request = reqlist[fileno].decode()[:-2]
                        self.logger.debug('Got a request: %s', request)
                        if request[:5] == requests.CLOSE:
                            self.logger.info('Got a close request, exiting')
                            self._manager.stop() if self._manager else None
                            epoll.modify(fileno, 0)  # Do not listen for next events on this socket
                            connlist[fileno].shutdown(socket.SHUT_RDWR)
                            epoll.unregister(self._socket.fileno())
                            epoll.close()
                            break
                        # Return array with True if request in requests, else return empty array
                        # and it will interpret as False
                        elif [True for i in [requests.PLAY,
                                             requests.STOP,
                                             requests.NEXT,
                                             requests.LIST,
                                             requests.PAUSE,
                                             requests.RETRY,
                                             requests.RESUME] if request[:len(i)] == i]:
                            self.logger.info('Process %s request', request.split(' ')[0])
                            self._manager = manager.Manager() if not self._manager else self._manager
                            self._manager.process(request)
                            reqlist[fileno] = b''
                        else:
                            self.logger.debug('Connection data is %s', reqlist[fileno].decode())
                            self.logger.info('Unknown request, pass')
                            reqlist[fileno] = b''
        except ValueError:
            self.logger.info('You try to epoll on closed epoll object. Was server ran in a thread?')
        finally:
            self.close()

    def getLogFileHandles(self, logger):
        """ Get a list of filehandle numbers from logger
            to be handed to DaemonContext.files_preserve
        """
        handles = []
        for handler in logger.handlers:
            handles.append(handler.stream.fileno())
        if logger.parent:
            handles += self.getLogFileHandles(logger.parent)
        return handles

    def run_detached(self):
        """Run server in detached mode"""
        with daemon.DaemonContext(files_preserve=self.getLogFileHandles(self.logger)) as d:
            self.logger.debug('Run server in daemon mode')
            self._daemon = d
            self.run()

    def close(self):
        """Properly shutdown daemon"""
        self.logger.debug('Closing server socket')
        self._socket.close()
        self.logger.debug('Server socket closed')
        if self._daemon:
            self.logger.debug('Shutdown daemon')
            self._daemon.close()

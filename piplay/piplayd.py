import daemon
import socket, select
import logging
from piplay import requests, manager

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-30s %(levelname)-9s %(message)s')


class Server:
    def __init__(self, address, port):
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
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(self.address)
        self._socket.listen(1)
        self._socket.setblocking(0)
        self.logger.debug('Start listening on %s:%s', *self.address)
        epoll = select.epoll()
        epoll.register(self._socket.fileno(), select.EPOLLIN)
        try:
            EOL = b'\n\n'
            connlist = {}
            reqlist = {}
            while True:
                events = epoll.poll(1)
                for fileno, event in events:
                    if fileno == self._socket.fileno():
                        clientconn, address = self._socket.accept()
                        clientconn.setblocking(0)
                        epoll.register(clientconn.fileno(), select.EPOLLIN)
                        connlist[clientconn.fileno()] = clientconn
                        reqlist[clientconn.fileno()] = b''

                    elif event and select.EPOLLIN:
                        while EOL not in reqlist[fileno]:
                            reqlist[fileno] += connlist[fileno].recv(2)
                        request = reqlist[fileno].decode()[:-2]
                        self.logger.debug('Got a request: %s', request)
                        if request[:5] == requests.CLOSE:
                            self.logger.info('Got a close request, exiting')
                            self._manager.stop() if self._manager else None
                            epoll.modify(fileno, 0)
                            connlist[fileno].shutdown(socket.SHUT_RDWR)
                            epoll.unregister(self._socket.fileno())
                            epoll.close()
                            break
                        elif request[:4] == requests.PLAY:
                            self.logger.info('Process play request')
                            self._manager = manager.Manager(request)
                            self._manager.process()
                            self._manager.play()
                            reqlist[fileno] = b''
                            pass
        except ValueError:
            self.logger.info('You try to epoll on closed epoll object. Was server ran in a thread?')
        finally:
            self.close()

    def run_detached(self):
        with daemon.DaemonContext() as d:
            self.logger.debug('Run server in daemon mode')
            self._daemon = d
            self.run()

    def close(self):
        self.logger.debug('Closing server socket')
        self._socket.close()
        self.logger.debug('Server socket closed')
        if self._daemon:
            self.logger.debug('Shutdown daemon')
            self._daemon.close()

#!/usr/bin/env python
"""Play music from some online sources

Usage:
    client.py [-v...] [-s SEARCH_QUERY] COMMAND
    client.py -h

Options:
    -v                          verbosity level. Use more than one time to raise
                                    level (like -vvvv)
    -h --help                   show this help
    -s --search SEARCH_QUERY    query to search

Arguments:
    COMMAND  command to process (play, stop, next, list)
"""
import logging
import socket
from docopt import docopt
from piplay.config import logging as plog


class PiplayClient:
    def __init__(self):
        self.logger = None
        self.args = None
        self._readOptions()
        self._connection = None

    @property
    def connection(self):
        if not self._connection:
            self._connection = socket.socket()
            self._connection.connect(('127.0.0.1', 33033))
        return self._connection

    def _readOptions(self):
        """ Reads command line options and saves it to self.args hash. Also set
        log level and logging message format
        """
        self.args = docopt(__doc__, version='0.2')
        # Set logging level. Log level in python logging lowers to 10 points
        # with each level, so we set it to 10 (maximum) in case of '-v'>5 and
        # higher it for less '-v's
        loglevel = (5 - self.args['-v'])*10 if self.args['-v'] < 5 else 10

        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler(plog.FILENAME)
        handler.setLevel(plog.LOGLEVEL)
        formatter = logging.Formatter(plog.LOGFORMAT)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        # We need next trick with list comprehension cause self.args stores
        # some '\n' symbols, so it badly formatted in logs by default
        self.logger.debug('Passed arguments is: %s', {k: v for k, v in self.args.items()})

    def runServer(self):
        from piplay import piplayd
        self.logger.debug('Starting daemon in detached mode')
        server = piplayd.Server('127.0.0.1', 33033)
        server.run_detached()

    def run(self):
        from piplay import piplayd
        self.logger.debug('Starting daemon')
        server = piplayd.Server('127.0.0.1', 33033)
        server.run()

    def stopServer(self):
        self.logger.debug('Sending close to daemon')
        self.connection.send(bytes('close\n\n', 'utf-8'))
        self.connection.close()

    def play(self, query=None):
        self.logger.debug('Sending play to daemon')
        self.connection.send(bytes('play {query}\n\n'.format(query=query), 'utf-8'))
        self.connection.close()

    def next(self):
        self.logger.debug('Sending next to daemon')
        self.connection.send(bytes('next\n\n', 'utf-8'))
        self.connection.close()

    def stop(self):
        self.logger.debug('Sending stop to daemon')
        self.connection.send(bytes('stop\n\n', 'utf-8'))
        self.connection.close()

    def list(self):
        self.logger.debug('Sending list to daemon')
        self.connection.send(bytes('list\n\n', 'utf-8'))
        self.connection.close()


if __name__ == "__main__":
    c = PiplayClient()
    if c.args['COMMAND'] == 'rundaemon':
        c.runServer()
    elif c.args['COMMAND'] == 'run':
        c.run()
    elif c.args['COMMAND'] == 'stopdaemon':
        c.stopServer()
    elif c.args['COMMAND'] == 'play':
        c.play(c.args['--search'])
    else:
        getattr(c, c.args['COMMAND'])()


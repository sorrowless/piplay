import logging
import vlc
from piplay import requests, config

logging.basicConfig(
    level=config.LOGLEVEL,
    format=config.LOGFORMAT)


class Manager:
    def __init__(self, request=None):
        self._cachepaths = []
        self.logger = logging.getLogger(__name__)
        self.request = request
        self.rtype = None
        self.rbody = None
        self.player = None
        self.storages = [storage for storage in config.STORAGES]

    def _strip_request(self):
        if self.request[:4] == requests.PLAY:
            self.rtype = requests.PLAY
            if self.request[4:] != self.rbody:
                self.rbody = self.request[4:]
                self._cachepaths = []
        elif self.request[:4] == requests.STOP:
            self.rtype = requests.STOP
        elif self.request[:4] == requests.NEXT:
            self.rtype = requests.NEXT
        elif self.request[:4] == requests.LIST:
            self.rtype = requests.LIST
        self.logger.debug('Request type is "%s"', self.rtype)
        self.logger.debug('Request body is "%s"', self.rbody)

    def fillCache(self):
        if not self._cachepaths:
            self.logger.debug('Cache is empty, ask storages to search "%s"', self.rbody)
            for storage in self.storages:
                self.logger.debug('Try %s', storage.__name__)
                self._cachepaths = storage.search(self.rbody)
                if self._cachepaths:
                    break

    def play(self):
        try:
            self.logger.debug('Try play from cached results')
            newpath = self._cachepaths.pop(0)
        except IndexError:
            self.fillCache()
            newpath = self._cachepaths.pop(0)
        if not self.player:
            self.logger.debug('Initialize new player')
            self.player = vlc.MediaPlayer(newpath['url'])
        else:
            self.player.set_mrl(newpath['url'])
        self.logger.debug('Send "%s - %s" to player', newpath['artist'], newpath['title'])
        self.player.play()

    def stop(self):
        self.logger.debug('Send stop to player')
        self.player.stop()

    def next(self):
        self.logger.debug('Send next to player')
        self.stop()
        self.play()

    def list(self):
        self.logger.debug('List of play queue from cache:')
        for row in self._cachepaths:
            self.logger.debug('%s - %s', row['artist'], row['title'])
        return self._cachepaths

    def process(self, request):
        self.logger.debug('Got request: %s', request)
        self.request = request
        self._strip_request()
        if self.rtype == requests.PLAY:
            self.play()
        elif self.rtype == requests.STOP:
            self.stop()
        elif self.rtype == requests.NEXT:
            self.next()
        elif self.rtype == requests.LIST:
            self.list()
        return self.player

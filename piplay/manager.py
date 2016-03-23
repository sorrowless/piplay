import logging
from piplay import requests, player
from piplay.config import logging as plog
from piplay.config import storage as pstor

logging.basicConfig(
    level=plog.LOGLEVEL,
    format=plog.LOGFORMAT,
    filename=plog.FILENAME)


class Manager:
    """Manage incoming requests - strip them and process"""
    def __init__(self, request=None):
        """Constructor

        :param request: Request to process
        """
        self._cachepaths = []
        self.logger = logging.getLogger(__name__)
        self.request = request
        self.rtype = None
        self.rbody = None
        self.player = None
        self.storages = [storage for storage in pstor.STORAGES]

    def _strip_request(self):
        """Split request to type and body"""
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
        elif self.request[:5] == requests.PAUSE:
            self.rtype = requests.PAUSE
        elif self.request[:5] == requests.RETRY:
            self.rtype = requests.RETRY
        elif self.request[:6] == requests.RESUME:
            self.rtype = requests.RESUME
        self.logger.debug('Request type is "%s"', self.rtype)
        self.logger.debug('Request body is "%s"', self.rbody)

    def fillCache(self):
        if not self._cachepaths:
            self.logger.debug('Cache is empty, ask storages to search "%s"', self.rbody)
            for storage in self.storages:
                self.logger.debug('Try %s', storage.__name__)
                self._cachepaths = storage.search(self.rbody)
                if self._cachepaths:
                    self.logger.info('Saved %s entries from %s storage to cache',
                                     len(self._cachepaths), storage.__name__)
                    break

    def play(self):
        try:
            self.logger.debug('Try play from cached results')
            newpath = self._cachepaths.pop(0)
        except IndexError:
            self.fillCache()
            if self._cachepaths:
                newpath = self._cachepaths.pop(0)
            else:
                self.logger.error("Can't fill cache from any storage. Sorry, we can't anything to process then")
                return 1
        if not self.player:
            self.logger.debug('Initialize new player')
            self.player = player.Player(newpath['url'])
        else:
            self.player.set_path(newpath['url'])
        self.logger.debug('Send "%s - %s" to player', newpath['artist'], newpath['title'])
        self.player.play()

    def stop(self):
        self.logger.debug('Send stop to player')
        self.player.stop()

    def pause(self):
        self.logger.debug('Send pause to player')
        self.player.pause()

    def resume(self):
        self.logger.debug('Send resume to player')
        self.player.resume()

    def retry(self):
        self.logger.debug('Send retry to player')
        self.player.retry()

    def next(self):
        self.logger.debug('Send next to player')
        if self.player:
            self.stop()
            self.play()

    def list(self):
        self.logger.debug('List of play queue from cache:')
        for row in self._cachepaths:
            self.logger.info('%s - %s', row['artist'], row['title'])
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
        elif self.rtype == requests.PAUSE:
            self.pause()
        elif self.rtype == requests.RESUME:
            self.resume()
        elif self.rtype == requests.RETRY:
            self.retry()
        return self.player

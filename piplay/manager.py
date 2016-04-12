import logging

from piplay import requests as rq
from piplay import player
from piplay.config import logging as plog
from piplay.config import storage as pstor
from piplay.notifications import Notification

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
        self.options = {}
        self.player = None
        self.storages = [storage for storage in pstor.STORAGES]
        self.notifier = Notification()

    def _strip_request(self):
        """Split request to type, body and options"""
        for request in self.request.splitlines():
            if request[:4] == rq.PLAY:
                self.rtype = rq.PLAY
                # if we don't try to fetch the same data
                if self.request[4:] != self.rbody:
                    self.rbody = str.strip(request[4:])
                    self.logger.debug('Request body is "%s"', self.rbody)
                    self._cachepaths = []
            elif [req for req in [rq.STOP,
                                  rq.NEXT,
                                  rq.LIST,
                                  rq.PAUSE,
                                  rq.RETRY,
                                  rq.RESUME,
                                  rq.STATUS] if request[:len(req)] == req]:
                self.rtype = request.split(' ')[0]
            else:
                keyvalue = request.split(' ')
                self.options[keyvalue[0]] = keyvalue[1]
        self.logger.debug('Request type is "%s"', self.rtype)

    def fillCache(self, resCountAsked):
        if not self._cachepaths:
            self.logger.debug('Cache is empty, ask storages to search "%s"',
                              self.rbody)
            for storage in self.storages:
                self.logger.debug('Try %s', storage.__name__)
                self._cachepaths = storage.search(self.rbody, resCountAsked)
                if self._cachepaths:
                    self.logger.info(
                        'Saved %s entries from %s storage to cache',
                        len(self._cachepaths), storage.__name__)
                    break
                else:
                    self.logger.debug(
                        '%s return 0 results, will try next storage',
                        storage.__name__)

    def play(self):
        if not self.player:
            self.logger.debug('Initialize new player')
            self.player = player.Player(statusCallback=self.status)
        self.player.set_options(**self.options)
        self.logger.debug('Try play from cached results')
        if not self._cachepaths:
            self.fillCache(self.options.get('count', 10))
            if not self._cachepaths:
                self.logger.error("Can't fill cache from any storage. Sorry, \
                                  we can't anything to process then")
                return 1
        self.logger.debug('Send found data to player')
        self.player.set_path(self._cachepaths)
        self.player.stop()
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
            self.player.next()

    def list(self):
        self.logger.debug('List of play queue from cache:')
        for row in self._cachepaths:
            self.logger.info('%s - %s', row['artist'], row['title'])
        return self._cachepaths

    def status(self, showLength=True):
        self.logger.debug('Asking status from player')
        if self.player:
            res = self.player.status()
        else:
            self.logger.debug('Current status is: player does not created yet')
            return 1
        for row in self._cachepaths:
            if row['url'] == res['mrl']:
                res['artist'] = row['artist']
                res['title'] = row['title']
        status = res['status']
        length = '%d:%d' % (res['length'] // 60,
                            res['length'] - res['length'] // 60 * 60)
        artist = res.get('artist', 'Unknown')
        title = res.get('title', 'Unknown')
        self.logger.info('Current status is: %s', status)
        self.logger.info('Track length: %s', length) if showLength else False
        self.logger.info('Artist: %s', artist)
        self.logger.info('Track title: %s', title)
        self.logger.info('Track url: %s', res.get('mrl', 'Unknown'))
        if showLength:
            self.notify(status, '%s - %s (%s)' % (artist, title, length))
        else:
            self.notify(status, '%s - %s' % (artist, title))

    def error(self):
        self.logger.debug('Unknown request type')
        self.notify('Error', 'Unknown request type')

    def process(self, request):
        self.logger.debug('Got request: %s', request)
        self.request = request
        self._strip_request()
        self.logger.debug('Process a request')
        getattr(self, self.rtype, self.error)()
        self.logger.debug('Process done')
        return self.player

    def notify(self, summary, message, icon=''):
        self.logger.debug('Prepare notification message')
        self.notifier.setInfo(summary, message, icon)
        self.notifier.show()

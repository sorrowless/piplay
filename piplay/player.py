import logging
import vlc
from piplay.config import logging as plog

logging.basicConfig(
    level=plog.LOGLEVEL,
    format=plog.LOGFORMAT,
    filename=plog.FILENAME
)


class Player:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.path = None
        self.pathdict = {}
        self.player = None
        try:
            self._list = vlc.MediaList()
            self.player = vlc.MediaListPlayer()
            self.player.set_media_list(self._list)
            self.player.event_manager().event_attach(
                vlc.EventType.MediaListPlayerNextItemSet,
                self.playInfo
            )
        except NameError:
            self.logger.error("Can't initialize vlc player instance. Missing libvlc in system?",
                              "Try to install VLC player")

    def set_path(self, path):
        if isinstance(path, list):
            self.logger.debug('Got %s new paths to play', len(path))
            self.pathdict = path
            self.logger.debug('Clear old tracklist')
            for i in range(self._list.count()):
                self._list.remove_index(0)
            self.logger.debug('Add new tracklist')
            for data in self.pathdict:
                self._list.add_media(data['url'])

        else:
            self.player = vlc.MediaPlayer()
            self.logger.debug('Got new path to play: %s', path)
            self.path = path
            self.player.set_mrl(self.path) if self.path else None

    def set_options(self, *args, **kwargs):
        pass

    def play(self):
        self.player.play() if self.player else None

    def stop(self):
        if self.player and self.player.is_playing():
            self.player.stop()

    def resume(self):
        self.play() if self.player else None

    def next(self):
        res = self.player.next() if self.player else None
        if res == -1:
            self.logger.info('End of queue reached. Start from very beginning')
            self.player.next()

    def playInfo(self, *args, **kwargs):
        self.logger.debug('PlayInfo method, args is %s, kwargs is %s' % (str(args), str(kwargs)))

    def pause(self):
        try:
            self.player.pause()
        except:
            self.logger("Can't pause this track, sorry")

    def retry(self):
        self.player.stop()
        self.player.play()

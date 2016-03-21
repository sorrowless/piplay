import logging
import vlc
from piplay import config

logging.basicConfig(
    level=config.LOGLEVEL,
    format=config.LOGFORMAT)


class Player:
    def __init__(self, path=None):
        self.logger = logging.getLogger(__name__)
        self.path = path
        self.player = None
        try:
            self.player = vlc.MediaPlayer(path)
        except NameError:
            self.logger.error("Can't initialize vlc player instance. Missing libvlc in system?",
                              "Try to install VLC player")

    def set_path(self, path):
        self.logger.debug('Got new path to play: %s', path)
        self.path = path
        self.player.set_mrl(self.path) if self.path else None

    def play(self):
        self.player.play() if self.player else None

    def stop(self):
        self.player.stop() if self.player else None




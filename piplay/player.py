import logging
import vlc
from piplay.config import logging as plog

logging.basicConfig(
    level=plog.LOGLEVEL,
    format=plog.LOGFORMAT,
    filename=plog.FILENAME
)


class Player:
    def __init__(self, statusCallback=None):
        self.logger = logging.getLogger(__name__)
        self.path = None
        self.pathdict = {}
        self.player = None
        self.trackstatus = statusCallback  # We want to notify only from Manager
        try:
            self._list = vlc.MediaList()
            self._player = vlc.MediaPlayer()
            self.player = vlc.MediaListPlayer()
            self.player.set_media_player(self._player)
            self.player.set_media_list(self._list)
            self.player.event_manager().event_attach(
                vlc.EventType.MediaListPlayerNextItemSet,
                self.playInfo
            )
        except NameError:
            self.logger.error("Can't initialize vlc player instance. Missing \
                              libvlc in system?",
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
        media = self._player.get_media()
        self.logger.debug('Play %s', media.get_mrl())
        self.trackstatus(showLength=False)

    def pause(self):
        try:
            self.player.pause()
        except:
            self.logger("Can't pause this track, sorry")

    def retry(self):
        self._player.stop()
        self._player.play()

    def status(self):
        """Return status of current track

        :return: Hash with information of current track
        :rtype: dict
        """
        res = {'mrl': '',
               'length': '',
               'status': 'Not exist'}
        if not self.player:
            return res

        media = self._player.get_media()
        if self.player.get_state() == vlc.State.Playing:
            res['status'] = 'Playing'
        elif self.player.get_state() == vlc.State.Stopped:
            res['status'] = 'Stopped'
        elif self.player.get_state() == vlc.State.Paused:
            res['status'] = 'Paused'
        elif self.player.get_state() == vlc.State.Opening:
            res['status'] = 'Start playing'
        else:
            self.logger.debug("We don't know such state. It is %s",
                              str(self.player.get_state()))
            res['mrl'] = ''
            res['length'] = 0
            res['status'] = 'Unknown'
            return res
        res['mrl'] = media.get_mrl()
        res['length'] = media.get_duration() // 1000  # in seconds
        self.logger.debug('Send status to manager')
        return res

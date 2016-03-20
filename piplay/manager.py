import vlc
from piplay import requests

class Manager:
    def __init__(self, request):
        self.request = request
        self.rtype = None
        self.rbody = None
        self.player = None

    def _strip_request(self):
        if self.request[:4] == requests.PLAY:
            self.rtype = requests.PLAY
            self.rbody = self.request[4:]

    def play(self):
        self.player = vlc.MediaPlayer('file:///tmp/ci.mp3')
        self.player.play()

    def stop(self):
        self.player.stop()

    def process(self):
        self._strip_request()
        return self.player
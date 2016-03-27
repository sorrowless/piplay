from hamcrest import *  # noqa

from piplay import player


class TestPlayer:
    def test_run(self):
        calling(player.run).with_args('test')

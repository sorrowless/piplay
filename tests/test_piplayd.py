import pytest
import socket
import threading
import time
from piplay import piplayd
from piplay import manager
from unittest.mock import patch
from hamcrest import *


class TestServer:
    def test_serveFail(self):
        """ Should fail if server created but not ran"""
        server = piplayd.Server('127.0.0.1', 33033)
        conn = socket.socket()
        with pytest.raises(ConnectionRefusedError):
            conn.connect(server.address)
        conn.close()

    def test_closeRequest(self):
        """ Should create server, run it and recieve connection"""
        server = piplayd.Server('127.0.0.1', 33033)
        s_thread = threading.Thread(target=server.run)
        s_thread.start()

        time.sleep(0.1)  # we need this sleep - other way server has not enough time to start and fails on connect
        conn = socket.socket()
        conn.connect(server.address)
        conn.send(b'close\n\n')
        conn.close()

        s_thread.join()

    @patch.object(manager.Manager, 'play', create_autospec=True)
    @patch.object(manager.Manager, 'stop', create_autospec=True)
    def test_playRequest(self, mockedPlay, mockedStop):
        """ Should create server, run it and play something"""
        server = piplayd.Server('127.0.0.1', 33033)
        s_thread = threading.Thread(target=server.run)
        s_thread.start()

        time.sleep(0.1)  # we need this sleep - other way server has not enough time to start and fails on connect
        conn = socket.socket()
        conn.connect(server.address)

        conn.send(bytes('play Сплин - Выхода нет\n\n', 'utf-8'))
        conn.send(b'close\n\n')
        conn.close()

        s_thread.join()


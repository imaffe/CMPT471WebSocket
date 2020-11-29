import unittest

from cmpt471ws.ws_core.websocket_helper import WebsocketHelper


class TestWebsocketHelper(unittest.TestCase):
    def test_read_string_line(self):
        line = 'dfsdfasdf \r\n asdf'
        s, line = WebsocketHelper.read_string_line(bytearray(line.encode('ascii')))
        self.assertTrue(s == bytearray('dfsdfasdf '.encode('ascii')))
        self.assertTrue(line == bytearray(' asdf'.encode('ascii')))

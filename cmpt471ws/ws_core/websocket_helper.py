import os
import socket

from cmpt471ws.ws_core.common import WebsocketCommon
from cmpt471ws.ws_core.websocket_impl import WebsocketImpl

class WebsocketHelper:

    def __init__(self):
        pass


    @classmethod
    def batch(cls, websocket_impl: WebsocketImpl):
        # TODO
        pass

    @classmethod
    def read(cls, ws_impl: WebsocketImpl, sock: socket.socket):
        # TODO this should always be non-blocking
        data = sock.recv(WebsocketCommon.DEFAULT_RCV_BUF_SIZE)
        if not data:
            pass
            # TODO we should log something here

        return data

    @classmethod
    def random_bytearray(cls, size: int):
        return  bytearray(os.urandom(size))


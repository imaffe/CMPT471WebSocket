import socket

from cmpt471ws.ws_core.common import WebsocketCommon
from cmpt471ws.ws_core.websocket_draft import WebsocketDraft
from cmpt471ws.ws_core.websocket_impl import WebsocketImpl


class WebsocketClient:
    def __init__(self, host, port):
        self.ws_impl = WebsocketImpl(self, WebsocketCommon.ROLE_CLIENT)
        self.host = host
        self.port = port
        self.draft = WebsocketDraft(WebsocketCommon.ROLE_CLIENT)
        # empty header at first
        self.headers = {}
        self.write_thread = WebsocketClientWriteThread(self)

        self.socket = socket.socket()




    def connect(self):
        """
        connect to the server by issueing a handshake request, this is a non-blocking method

        :return:
        """
        self.socket.connect((self.host, self.port))





        # TODO close the socket gracefully

    def close(self):
        pass


    def send(self, message: str):
        """
        message is a string
        :param data:
        :return:
        """
        pass

    # TODO this dispatcher might be too slow
    def send(self, data: bytearray):
        pass


    def run(self):
        """
        start the client, begin read loop
        :return:
        """
        pass


    def _send_handshake(self):
        """

        :return:
        """


    def on_websocket_message(self, message: str):
        pass


    def on_message(self, message: str):
        pass



    def on_websocket_open(self, handshake):
        pass


    def on_open(self, handshake):
        pass

    # we will ignore close for now




class WebsocketClientWriteThread:
    def __init__(self, websocket_client: WebsocketClient):
        self.websocket_client = websocket_client


import select, socket, sys

from cmpt471ws.ws_core.websocket_impl import WebsocketImpl


class WebsocketServer:
    LISTEN_QUEUE_SIZE = 5
    def __init__(self, websocket_impl : WebsocketImpl, port : int, host: str):
        self.websocket_impl = websocket_impl
        self.port = port
        self.host = host




    def shutdown(self):
        pass

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0) # non-blocking TCP socket
        self.socket.bind(self.host, self.port)
        self.socket.listen(WebsocketServer.LISTEN_QUEUE_SIZE)

        self.input_sockets = [self.socket]
        self.output_sockets = []
        self.message_queues = {}
        
        # start listener thread
        while inputs:


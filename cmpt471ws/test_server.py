from cmpt471ws.ws_core.websocket_impl import WebsocketImpl
from cmpt471ws.ws_core.websocket_server import WebsocketServer


def main():
    server = ChatServer("127.0.0.1", 8100)
    server.start()
    print("chat server started")




class ChatServer(WebsocketServer):
    def __init__(self, host, port):
        WebsocketServer.__init__(self, host, port)

    def on_open(self, ws_impl: WebsocketImpl):
        print("Server on_open() called, connection established")
        self.broadcast("Server got a new connection")
        # TODO server currently  do not support send



    def on_message(self, ws_impl: WebsocketImpl, message):
        print("Server received message:", message)
        self.broadcast("server got your message, this is a broad cast message LOL")


    def on_close(self):
        pass

if __name__ == '__main__':
    main()


from cmpt471ws.ws_core.websocket_client import WebsocketClient
from cmpt471ws.ws_core.websocket_impl import WebsocketImpl


def main():
    client = ChatClient("127.0.0.1", 8100)

    # TODO we can make this blocking
    print("trying to connect")
    client.connect()
    client.send("Hello from Affe client")

class ChatClient(WebsocketClient):
    def __init__(self, host, port):
        WebsocketClient.__init__(self, host, port)

    def on_message(self, ws_impl, message: str):
        pass

    def on_open(self, ws_impl, handshake):
        print("Client: Websocket Connect Success")


if __name__ == '__main__':
    main()


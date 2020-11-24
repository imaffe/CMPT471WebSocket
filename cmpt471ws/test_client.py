from cmpt471ws.ws_core.websocket_client import WebsocketClient




def main():
    client = ChatClient("127.0.0.1", 8100)

    # TODO we can make this blocking
    client.connect()




class ChatClient(WebsocketClient):
    def __init__(self, host, port):
        WebsocketClient.__init__(self, host, port)

    def on_message(self, message: str):
        pass


    def on_open(self, handshake):
        pass






if __name__ == '__main__':
    main()


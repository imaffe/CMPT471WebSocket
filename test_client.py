from cmpt471ws.ws_core.websocket_client import WebsocketClient
from cmpt471ws.ws_core.websocket_impl import WebsocketImpl

import argparse
import random
import string

def main():
    try:
        client = ChatClient(args.ip, args.port)

        # TODO we can make this blocking
        print("trying to connect")
        client.connect()
        for msg in args.message:
            client.send(msg)
            print(f'Client sent message: {msg}')

        client.close()
        print('-------------------------------\nthis endth the test\n')
    except Exception as e:
        raise e

class ChatClient(WebsocketClient):
    def __init__(self, host, port):
        WebsocketClient.__init__(self, host, port)

    def on_message(self, ws_impl, msg: str):
        print("Client: received message from server:{}".format(msg))

    def on_open(self, ws_impl, handshake):
        print("Client: Websocket Connect Success")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Socket Client!')
    parser.add_argument('-ip', '--ip', dest='ip', type=str, action='store', default='127.0.0.1', required=False, help='IP address')
    parser.add_argument('-p', '--p', dest='port', type=int, action='store', default=8100, required=False, help='Port number')
    parser.add_argument('-m', '--message', dest='message', type=str, default=['Client Test Message'], nargs='+', action='store', required=False, help='Client send message')
    parser.add_argument('-t', '--test', dest='test', type=int, default=0, action='store', required=False, help='Test index')
    
    args = parser.parse_args()
    
    if args.test == 0:
        pass
    elif args.test == 1:
        args.message = []
        for i in range(20):
            msg_size = random.randint(10, 100)
            msg = ''.join(random.choices(string.ascii_uppercase + string.digits, k=msg_size))
            args.message.append(msg)
    elif args.test == 2:
        args.message = []
        for i in range(20):
            msg_size = random.randint(300, 1000)
            msg = ''.join(random.choices(string.ascii_uppercase + string.digits, k=msg_size))
            args.message.append(msg)

    main(args)
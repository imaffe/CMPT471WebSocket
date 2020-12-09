from cmpt471ws.ws_core.websocket_impl import WebsocketImpl
from cmpt471ws.ws_core.websocket_server import WebsocketServer

import argparse
import random
import string

count = 1

def main(args):
    print("chat server starting\n")
    server = ChatServer(args.ip, args.port)
    server.start()
    print("chat server started\n")

    print('-------------------------------\nthis endth the test\n')

class ChatServer(WebsocketServer):
    def __init__(self, host, port):
        WebsocketServer.__init__(self, host, port)

    def on_open(self, ws_impl):
        print("Server on_open() called, connection established\n")
        self.broadcast("Server got a new connection")
        # TODO server currently  do not support send

    def on_message(self, ws_impl, message):
        global count
        print("Server received message:", message + "\n")
        ws_impl.send(f'Server respond message: {args.respond} {count}')
        self.broadcast(f'Server broadcast message: {args.broadcast}')
        count = count+1

    def on_close(self, ws_impl):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Socket Server!')
    parser.add_argument('-ip', '--ip', dest='ip', type=str, action='store', default='127.0.0.1', required=False, help='IP address')
    parser.add_argument('-p', '--p', dest='port', type=int, action='store', default=8100, required=False, help='Port number')
    parser.add_argument('-r', '--respond', dest='respond', type=str, default='Server Test Respond', action='store', required=False, help='Server respond message')
    parser.add_argument('-b', '--broadcast', dest='broadcast', type=str, default='Server Test Broadcast', action='store', required=False, help='Server broadcast message')
    parser.add_argument('-t', '--test', dest='test', type=int, action='store', required=False, help='Test index')
    
    args = parser.parse_args()

    if args.test == 0:
        pass
    elif args.test == 1:
        args.respond = ''.join(random.choices(string.ascii_uppercase + string.digits, k=1000))
        print(args.respond)
    elif args.test == 2:
        args.broadcast = ''.join(random.choices(string.ascii_uppercase + string.digits, k=1000))

    main(args)


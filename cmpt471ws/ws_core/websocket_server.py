import select, socket, sys, selectors

from cmpt471ws.ws_core.websocket_impl import WebsocketImpl


class WebsocketServer:
    LISTEN_QUEUE_SIZE = 5
    LISTEN_SOCKET_ID = "sys-listen-socket"
    def __init__(self, websocket_impl : WebsocketImpl, port : int, host: str):
        self.websocket_impl = websocket_impl
        self.port = port
        self.host = host




    def shutdown(self):
        pass

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False) # non-blocking TCP socket
        self.socket.bind(self.host, self.port)
        self.socket.listen(WebsocketServer.LISTEN_QUEUE_SIZE)

        # self.input_sockets = [self.socket]
        # self.output_sockets = []
        # self.message_queues = {}
        
        # use selector module instead of select directly
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.socket, selectors.EVENT_READ, WebsocketServer.LISTEN_SOCKET_ID)

        self.running_status = "RUNNING" # change to use enum

        while self.running_status == "RUNNING":
            events = self.selector.select()
            for key, event_type in events:
                self.dispatch(key, event_type)



    def dispatch(self, key, event_type):

        if key.data == WebsocketServer.LISTEN_SOCKET_ID:
            # this is the accept sockets
            self.do_accept(key, event_type)
            return
        else:
            # client sent message to server, handle read
            self.do_read(key,event_type)


    # called everytime a new client is trying to connect to current server
    def do_accept(self, key, event_type):
        assert key.data == WebsocketServer.LISTEN_SOCKET_ID
        conn, addr = key.fileobj.accept()
        conn.setblocking(False)

        assert event_type != selectors.EVENT_WRITE
        # create a WebsocketImpl and associate it with the key
        websocket_impl = WebsocketImpl(self)

        # add the socket corresponding to the new client to the selector
        selection_key = self.selector.register(conn, selectors.EVENT_READ, websocket_impl)
        websocket_impl.set_key(selection_key)
        websocket_impl.set_wrapped_socket(conn)

        # TODO we can add some buffer implementation here, increase buffer size for each new client

    def do_read(self, key, event_type):
        assert event_type != selectors.EVENT_WRITE












    def do_accept(self):
        pass


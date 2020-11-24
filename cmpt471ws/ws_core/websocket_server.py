import selectors
import socket
from threading import Thread

from cmpt471ws.ws_core.common import WebsocketCommon
from cmpt471ws.ws_core.websocket_helper import WebsocketHelper
from cmpt471ws.ws_core.websocket_impl import WebsocketImpl


class WebsocketServer:
    # TODO refactor these fields so each server can have different configurations
    LISTEN_QUEUE_SIZE = 5
    LISTEN_SOCKET_ID = "sys-listen-socket"
    CONCURRENT_DECODER_NUM = 6
    def __init__(self,
                 port: int,
                 host: str,
                 ):
        self.websocket_impl = WebsocketImpl(self, WebsocketCommon.ROLE_SERVER)
        self.port = port
        self.host = host
        self.executors_nums = WebsocketServer.CONCURRENT_DECODER_NUM
        self.listen_queue_size = WebsocketServer.LISTEN_QUEUE_SIZE


    def shutdown(self):
        pass

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False) # non-blocking TCP socket
        self.socket.bind((self.host, self.port))
        self.socket.listen(self.listen_queue_size)

        # self.input_sockets = [self.socket]
        # self.output_sockets = []
        # self.message_queues = {}

        # use selector module instead of select directly
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.socket, selectors.EVENT_READ, WebsocketServer.LISTEN_SOCKET_ID)

        # use to track how many times we assign a new client an executor
        self.queue_invoke_times = 0
        # initialize executors
        self.executors = []
        for i in range(self.executors_nums):
            self.executors.append(WebsocketServer.WebsocketWorker())

        self.running_status = "RUNNING" # change to use enum


        main_thread = Thread(target=self.server_loop())
        main_thread.start()

        # spawn executor threads
        for exec in self.executors:
            exec.start()


        # merge these thread, we might have concurrency issues
        main_thread.join()

        for exec in self.executors:
            exec.join()




    def server_loop(self):
        while self.running_status == "RUNNING":
            events = self.selector.select()
            for key, event_type in events:
                self.dispatch(key, event_type)


    def dispatch(self, key, event_type):

        if key.data == WebsocketServer.LISTEN_SOCKET_ID:
            # this is the accept sockets
            self.do_accept(key, event_type)
            return
        elif event_type & selectors.EVENT_READ:
            # client sent message to server, handle read
            self.do_read(key, event_type)
        elif event_type & selectors.EVENT_WRITE:
            self.do_write(key, event_type)


    # called everytime a new client is trying to connect to current server
    def do_accept(self, key, event_type):
        assert key.data == WebsocketServer.LISTEN_SOCKET_ID
        conn, addr = key.fileobj.accept()
        conn.setblocking(False)

        assert event_type & selectors.EVENT_WRITE
        # create a WebsocketImpl and associate it with the key
        websocket_impl = WebsocketImpl(self)

        # add the socket corresponding to the new client to the selector
        selection_key = self.selector.register(conn, selectors.EVENT_READ, websocket_impl)
        websocket_impl.set_key(selection_key)
        websocket_impl.set_wrapped_socket(conn)

        # TODO we can add some buffer implementation here, increase buffer size for each new client

    def do_read(self, key, event_type):
        assert event_type & selectors.EVENT_READ
        ws_impl = key.data

        # retrieve the socket from ws_impl
        sock = ws_impl.wrapped_socket
        # read data from socket
        data = WebsocketHelper.read(ws_impl, sock)
        assert data is not None
        size = len(data)
        assert size > 0


        ws_impl.put_inqueue(data)
        self.assign_executor(ws_impl)
        # TODO potentially we will use a global thread pool, instead of using per ws_impl thread




    # TODO we are not handling any error here , should we add err handling code ?
    def do_write(self, key, event_type):
        ws_impl = key.data
        assert isinstance(ws_impl, WebsocketImpl)

        # flush message for this ws_impl to network
        WebsocketHelper.batch(ws_impl)
        # reset the interested event to READ
        new_key = self.selector.modify(ws_impl.wrapped_socket, selectors.EVENT_READ, ws_impl)

        # update the ws_impl's key
        ws_impl.set_key(new_key)


    def on_write_demand(self, ws_impl: WebsocketImpl):
        # This method actually do the write job
        fileobj = ws_impl.wrapped_socket

        # need to register READ | WRITE events for this socket
        new_key = self.selector.modify(fileobj, selectors.EVENT_WRITE | selectors.EVENT_READ, ws_impl)
        ws_impl.set_key(new_key)

        # in java version, they called a selector.wakeup(), but we didn't found corresponding method
        # perhaps the modfiy would restart the select() execution


    def assign_executor(self, ws_impl: WebsocketImpl):
        if ws_impl.executor is None:
            ws_impl.set_executor(self.executors[self.queue_invoke_times % self.executors_nums])
            self.queue_invoke_times += 1
        ws_impl.executor.put_ws_queue(ws_impl)


    ### handshake
    def on_handshake_as_server(self):
        """
        :return: handshake response
        """
        # TODO
        pass

    def on_handshake_as_client(self):
        print("error on_handshake_as_client called by a server")
        return None


    ### The following method are callbacks exposed to WebsocketImpl,

    def on_websocket_message(self, ws_impl : WebsocketImpl, message):
        pass

    def on_websocket_open(self, ws_impl : WebsocketImpl, message):
        pass

    def on_websocket_close(self, ws_impl : WebsocketImpl, message):
        pass
    ### The following method should be exposed to user applications and should be overwritten

    # sync
    def broadcast(self, data):
        pass

    # callbacks that should be overriden
    def on_message(self, ws_impl: WebsocketImpl, message):
        pass

    def on_open(self):
        pass

    def on_close(self):
        pass



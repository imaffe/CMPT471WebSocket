import socket
from threading import Thread

from cmpt471ws.ws_core.client_handshake import ClientHandshake
from cmpt471ws.ws_core.common import WebsocketCommon
from cmpt471ws.ws_core.server_handshake import ServerHandshake
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

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



    def connect(self):
        """
        connect to the server by issueing a handshake request, this is a non-blocking method

        :return:
        """

        # TODO should use blocking mode in client
        self.socket.setblocking(True)
        # Timeout defaults to 500 ms
        self.socket.settimeout(500)
        try:
            self.socket.connect((self.host, self.port))

        except Exception as e:
            print(e)
            print("Error while trying to connect to Websocket Server\n")
            self.socket.close()
            return

        print("client connect success, trying to send handshakes")
        self._send_handshake()

        # start the write thread
        write_thread = Thread(target=self.write_thread)
        write_thread.start()
        try:
            while not self.is_closing() and not self.is_closed():
                data = self.socket.recv(WebsocketCommon.DEFAULT_RCV_BUF_SIZE)
                if len(data) == 0:
                    break
                else:
                    self.ws_impl.decode(data)
            # TODO close the socket
            # The write ends
            self.close_ws_connection()
        except:
            print("Error while reading from the socket\n")
            self.socket.close()



        # TODO close the socket gracefully
        write_thread.join()

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
        """
        sends out a byte array
        :param data:
        :return:
        """
        pass


    def run(self):
        """
        start the client, begin read loop
        :return:
        """
        pass


    def _send_handshake(self):
        """
        Sends handshake frames
        :return:
        """
        # hardcode the path here
        path = "127.0.0.1:8001/"

        client_handshake = ClientHandshake()
        client_handshake.resource_descriptor = path
        assert isinstance(self.host, str)
        host_and_port = self.host + str(self.port)
        client_handshake.put("Host", host_and_port)
        # Add headers to the handshake
        for key, value in self.headers.items():
            client_handshake.put(key, value)

        self.ws_impl.start_handshake(client_handshake)

    # needs to be override by user application
    def on_open(self, ws_impl: WebsocketImpl, handshake):
        pass

    def on_message(self, ws_impl: WebsocketImpl, message: str):
        pass

    def on_close(self, ws_impl: WebsocketImpl, message: str):
        pass

    # needs to be implemented as listener
    def on_websocket_open(self, ws_impl: WebsocketImpl,  handshake):
        assert isinstance(handshake, ServerHandshake)
        self.on_open(ws_impl, handshake)

    def on_websocket_message(self, ws_impl: WebsocketImpl, message: str):
        self.on_message(ws_impl, message)

    def on_websocket_close(self, ws_impl: WebsocketImpl, message):
        self.on_close(ws_impl, message)

    def on_handshake_as_server(self):
        print("error on_handshake_as_server called by a client\n")
        return None

    def on_handshake_as_client(self):
        pass

    def on_write_demand(self, ws_impl: WebsocketImpl):
        """
        Since this is client, write demand doesn't need to do anything
        :return:
        """
        pass

    # we will ignore close for now

    def close_ws_connection(self):
        """
        This sends out close frame to the server, we can ignore this for now
        :return:
        """
        # TODO
        pass


    def is_closing(self):
        return self.ws_impl.is_closing()

    def is_closed(self):
        return self.ws_impl.is_closed()




    def write_thread(self):
        try:
            while not self.is_closed() and self.is_closing():
                # TODO here the data is already encodes
                write_data = self.ws_impl.get_outqueue()
                assert isinstance(write_data, bytearray)
                # TODO we must guarantee that every byte in write_data is sent, thus the use of sendall()
                self.socket.sendall(write_data)

        except:
            # TODO we should be closing the socket
            self.socket.close()
            print("Error while writing to socket\n")




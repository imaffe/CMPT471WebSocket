
import queue
from typing import List

from cmpt471ws.ws_core.base_handshake import BaseHandshake
from cmpt471ws.ws_core.client_handshake import ClientHandshake
from cmpt471ws.ws_core.common import WebsocketCommon
from cmpt471ws.ws_core.server_handshake import ServerHandshake
from cmpt471ws.ws_core.websocket_draft import WebsocketDraft
from cmpt471ws.ws_core.websocket_exceptions import WebsocketDecodeError


class WebsocketImpl:
    # some default values
    def __init__(self, listener, role):
        # socket
        self.listener = listener
        # TODO should we have a limit for queue size?
        self.out_queue = queue.Queue()
        self.in_queue = queue.Queue()
        # Client or Server TODO refactor this to use enum
        self.role = role
        # selection key
        self.key = None
        # socket fileobj
        self.wrapped_socket = None
        # executor assigned
        self.executor = None

        # each draft a decoder
        self.draft = WebsocketDraft(role)

        self.resource_descriptor = None

        # The following attributes are necessary for managing websocket protocol states
        self.ready_state = WebsocketCommon.STATE_NOT_YET_CONNECTED

    def set_key(self, selection_key):
        self.key = selection_key

    def set_wrapped_socket(self, wrapped_socket):
        self.wrapped_socket = wrapped_socket

    def set_executor(self, executor):
        self.executor = executor

    def put_inqueue(self, data):
        self.in_queue.put(data)

    def get_inqueue(self):
        return self.in_queue.get(True, None)

    def put_outqueue(self, data):
        self.out_queue.put(data)

    def get_outqueue(self):
        # TODO should this be blocking ? yes
        return self.out_queue.get(True, None)

    """
    Actually the implementation here is a bit confusing, cause we delegate the decoding of data frames to
    the WebsocketProtocolImpl class, on the other hand, the decoding of handshake is implemented within this
    class. Still wondering why would we do this~ 
    """
    def decode(self, data):
        assert data is not None
        assert len(data) > 0

        if self.ready_state != WebsocketCommon.STATE_NOT_YET_CONNECTED:
            if self.ready_state == WebsocketCommon.STATE_OPEN:
                self.decode_frames(data)
        else:
            # we are still decoding handshake
            handshake_result, remaining = self.decode_handshake(data)
            # we need to know how many data are left
            if handshake_result and not self.is_closing() and not self.is_closed():
                assert remaining is not None
                # There are some other assertions, as we start to implement more
                if len(remaining) > 0:
                    self.decode_frames(data)


    def decode_frames(self, data):
        pass

    # this method should return if the handshake decodeing has completed, and if completed how many bytes

    # TODO it seems like using exception might be the best way to do IncompleteException
    def decode_handshake(self, data):
        """
        :param data:
        :return: result of the decode, true or false
        """
        return_data = data
        if self.role == WebsocketCommon.ROLE_SERVER:
            handshake, return_data = self.draft.translate_handshake(return_data)

            if handshake is None:
                # incomplete packet, need to do something
                return None, data

            if not isinstance(handshake, ClientHandshake):
                print("error server received non ClientHandshake\n")

            handshake_state = self.draft.accept_handshake_as_server(handshake)

            # check the handshake status
            if handshake_state == WebsocketCommon.HANDSHAKE_STATE_MATCHED:
                self.resource_descriptor = handshake.resource_descriptor
                response = self.listener.on_handshake_as_server()
                if response is None:
                    print("error when server listener build handshake response\n")
                    return False, data

                # we need the tmp response to add AOP features
                response_handshake = self.draft.post_process_handshake_repsonse_as_server(handshake, response)

                if isinstance(response_handshake, WebsocketDecodeError):
                    return False, data

                handshake_bytearrays = self.draft.create_handshake(response_handshake)
                # call open and inform listener
                self.write(handshake_bytearrays)
                self.open(handshake)
                # TODO what to return here
                return True, return_data
            else:
                # TODO still not complete, move on
                pass

        elif self.role == WebsocketCommon.ROLE_SERVER:
            pass
        else:
            # TODO should raise exception
            print("invalid role\n")


    # common funcionality
    # TODO how python defines typing
    # TODO how does python supports overloading
    def write(self, data_list: List[bytearray]):
        """
        Write the list of byte array to the underlying tunnel using using the queue,
        must be thread-safe. Talks to the upper layer client or server
        :param data_list:
        :return:
        """
        if data_list is None or len(data_list) == 0:
            print("WebsocketImpl#write() : trying to write empty data list or none")
            return
        for data in data_list:
            self.put_outqueue(data)
            # inform the client or server
            self.listener.on_write_demand(self)

    # TODO is it ok to use it this way ?
    def open(self, handshake: BaseHandshake):
        self.ready_state = WebsocketCommon.STATE_OPEN
        # TODO why pass self to it
        result = self.listener.on_websocket_open(self, handshake)
        if not result:
            print("on_websokcet_open failed\n")

    # The following method is for Closing a websocket session gracefully, include CLOSE frames.
    def is_closing(self):
        return self.ready_state == WebsocketCommon.STATE_CLOSING

    def is_closed(self):
        return self.ready_state == WebsocketCommon.STATE_CLOSED

    # For clients only
    def start_handshake(self, handshake: ClientHandshake):
        # TO
        handshake_req = self.draft.post_process_handshake_request_as_client(handshake)

        # TODO should notify the listener that the handshake has been sent, ignore this for now

        # send the handshake to
        handshake_bytearrays = self.draft.create_handshake(handshake_req)
        self.write(handshake_bytearrays)







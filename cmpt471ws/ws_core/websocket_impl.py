
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

        self.client_handshake = None

        self.tmp_handshake_data = bytearray()

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

    def get_outqueue_nonblock(self):
        try:
            result = self.out_queue.get(False, None)
            return result
        except queue.Empty as e:
            return None

    """
    Actually the implementation here is a bit confusing, cause we delegate the decoding of data frames to
    the WebsocketProtocolImpl class, on the other hand, the decoding of handshake is implemented within this
    class. Still wondering why would we do this~ 
    """
    def decode(self, data):
        assert data is not None
        # TODO if less than 0 it should not be passed here
        assert len(data) > 0
        # TODO we assume that handshake and send data is two isolated phase, if the previous
        # TODO is not complete then no data packets will be received
        if self.ready_state != WebsocketCommon.STATE_NOT_YET_CONNECTED:
            if self.ready_state == WebsocketCommon.STATE_OPEN:
                self.decode_frames(data)
        else:
            # we are still decoding handshake
            self.tmp_handshake_data.extend(data)
            handshake_result, remaining = self.decode_handshake(self.tmp_handshake_data)
            print("WS_IMPL: handshake success, moving trying to finish whole decode")
            # if handshake_result is None, means we need more packet
            if handshake_result is None:
                # TODO remaining is not changed if something wrong happens
                self.tmp_handshake_data = remaining
                return

            # we need to know how many data are left
            if handshake_result and not self.is_closing() and not self.is_closed():
                assert remaining is not None
                # There are some other assertions, as we start to implement more
                if len(remaining) > 0:
                    print("WS_IMPL: continueing decode frames after handshake complete")
                    # clera the handshake buffer
                    self.tmp_handshake_data = bytearray()
                    self.decode_frames(data)
            else:
                # TODO something wrong happens, reset to previous buffers, need to inform upper layer
                print("Error decoding, exit server")
                self.tmp_handshake_data = remaining


    def decode_frames(self, data):
        print("WS_IMPL: decode_frames get called")
        frames = self.draft.translate_frames(data)
        assert frames is not None

        for f in frames:
            result = self.draft.process_frame(self, f)
            # TODO what to do when exceptions happens ?
            print("WS_IMPL:  processes one frame")
            if not result:
                print("Error while process frames")
                return

    # this method should return if the handshake decodeing has completed, and if completed how many bytes

    # TODO it seems like using exception might be the best way to do IncompleteException
    def decode_handshake(self, data):
        """
        :param data:
        :return: result of the decode, true or false
        """
        return_data = data
        if self.role == WebsocketCommon.ROLE_SERVER:
            print("WS_IMPL: received server handshake data: {}".format(data.decode('ascii')))
            handshake, return_data = self.draft.translate_handshake(return_data)

            if handshake is None:
                # incomplete packet, need to do something
                return None, data

            if not isinstance(handshake, ClientHandshake):
                print("error server received non ClientHandshake: type {} {}".format(type(handshake), handshake.message))

            handshake_state = self.draft.accept_handshake_as_server(handshake)

            # check the handshake status
            if handshake_state == WebsocketCommon.HANDSHAKE_STATE_MATCHED:
                self.resource_descriptor = handshake.resource_descriptor
                response = self.listener.on_handshake_as_server()
                if response is None:
                    print("error when server listener build handshake response\n")
                    return False, data

                # we need the tmp response to add AOP features
                print("WS_IMPL: start handshake response post process")
                response_handshake = self.draft.post_process_handshake_repsonse_as_server(handshake, response)

                if isinstance(response_handshake, WebsocketDecodeError):
                    print("Error: {}".format(response_handshake.message))
                    return False, data
                print("WS_IMPL: ready to send handshake back")
                handshake_bytearrays = self.draft.create_handshake(response_handshake)
                # call open and inform listener
                print("WS_IMPL: ready to write server handshake")
                self.write(handshake_bytearrays)
                print("WS_IMPL: write complete")
                self.open(handshake)
                # TODO what to return here
                return True, return_data
            else:
                # TODO still not complete, move on
                print("Error handshake not in Match state, close connection")
                return False, data

        elif self.role == WebsocketCommon.ROLE_CLIENT:
            handshake, return_data = self.draft.translate_handshake(return_data)

            if handshake is None:
                # incomplete packet, need to do something
                return None, data

            if not isinstance(handshake, ServerHandshake):
                print("error client received non ServerHandhshake")
            handshake_state = self.draft.accept_handshake_as_client(self.client_handshake, handshake)
            # check the handshake status
            if handshake_state == WebsocketCommon.HANDSHAKE_STATE_MATCHED:
                response = self.listener.on_handshake_as_client()
                if response is None:
                    print("error when server listener build handshake response\n")
                    return False, data

                self.open(handshake)
                # TODO what to return here
                return True, return_data
            else:
                # TODO still not complete, move on
                print("Error handshake not in Match state, close connection")
                return False, data
        else:
            # TODO should raise exception
            print("invalid role\n")
            return False, data


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
        self.listener.on_websocket_open(self, handshake)
        # if not result:
        #     print("on_websocket_open failed\n")

    # The following method is for Closing a websocket session gracefully, include CLOSE frames.
    def is_closing(self):
        return self.ready_state == WebsocketCommon.STATE_CLOSING

    def is_closed(self):
        return self.ready_state == WebsocketCommon.STATE_CLOSED

    def is_open(self):
        return self.ready_state == WebsocketCommon.STATE_OPEN

    # For clients only
    def start_handshake(self, handshake: ClientHandshake):
        print("WS_IMPL: starting handshake")
        # TO
        handshake_req = self.draft.post_process_handshake_request_as_client(handshake)
        self.client_handshake = handshake_req
        # TODO should notify the listener that the handshake has been sent, ignore this for now

        # send the handshake to
        handshake_bytearrays = self.draft.create_handshake(handshake_req)
        self.write(handshake_bytearrays)

    # data plane sends

    def send(self, message):
        """
        This one calls send(frames) to send out data
        :param message:
        :return:
        """
        # TODO
        frames = self.draft.create_text_frames(message)
        self._send_frames(frames)

    def _send_frames(self, frames):
        # is the socket open ?
        if not self.is_open():
            print("connection has closed, not sending anything")
            return

        assert frames is not None, "send frames has input None frame"
        data_list = []
        for frame in frames:
            data_list.append(self.draft.create_bytearray_for_frame(frame))

        self.write(data_list)









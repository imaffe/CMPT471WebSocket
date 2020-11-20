
import queue

# TODO this class corresponds to a Protocol Instance
class WebsocketImpl:
    # some default values
    DEFAULT_PORT = 80

    # role enums
    ROLE_SERVER = "server"
    ROLE_CLIENT = "client"
    # connect state enums
    STATE_NOT_YET_CONNECTED = 100
    STATE_OPEN = 101
    STATE_CLOSING = 102
    STATE_CLOSED = 103

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


        # The following attributes are necessary for managing websocket protocol states
        self.ready_state = WebsocketImpl.STATE_NOT_YET_CONNECTED
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
    # TODO this can be refactored to use decode data
    def decode(self, data):
        assert data is not None
        assert len(data) > 0

        if self.ready_state != WebsocketImpl.STATE_NOT_YET_CONNECTED:
            if self.ready_state == WebsocketImpl.STATE_OPEN:
                self.decodeFrames(data)
        else:
            # we are still decoding handshake
            handshake_result, remaining = self.decodeHandshake(data)
            # we need to know how many data are left
            if handshake_result and not self._isClosing() and not self._isClosed():
                assert remaining is not None
                # There are some other assertions, as we start to implement more
                if len(remaining) > 0:
                    self.decodeFrames(data)


    def decodeFrames(self, data):
        pass


    # this method should return if the handshake decodeing has completed, and if completed how many bytes
    # we used in current data.

    def decodeHandshake(self, data):
        pass


    ### The following method is for Closing a websocket session gracefully, include CLOSE frames.

    def _isClosing(self):
        return self.ready_state == WebsocketImpl.STATE_CLOSING

    def _isClosed(self):
        return self.ready_state == WebsocketImpl.STATE_CLOSED







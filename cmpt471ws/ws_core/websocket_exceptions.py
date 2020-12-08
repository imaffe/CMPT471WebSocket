


class WebsocketDecodeError(Exception):
    def __init__(self, message, data=None):
        self.message = message
        self.data=data

class WebsocketInvalidFrameError(Exception):
    def __init__(self, message, data=None):
        self.message = message
        self.data=data

class WebsocketIncompletePacketError(Exception):
    def __init__(self, message, data=None):
        self.message = message
        self.data=data

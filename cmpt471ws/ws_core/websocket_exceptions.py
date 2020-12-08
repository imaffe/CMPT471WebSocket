


class WebsocketDecodeError(Exception):
    def __init__(self, message):
        self.message = message

class WebsocketInvalidFrameError(Exception):
    def __init__(self, message):
        self.message = message

class WebsocketIncompletePacketError(Exception):
    def __init__(self, message):
        self.message = message

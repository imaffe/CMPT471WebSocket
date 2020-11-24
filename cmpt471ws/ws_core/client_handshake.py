from cmpt471ws.ws_core.base_handshake import BaseHandshake


class ClientHandshake(BaseHandshake):
    def __init__(self):
        BaseHandshake.__init__()
        self.resource_descriptor = None


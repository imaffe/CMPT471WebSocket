from cmpt471ws.ws_core.base_handshake import BaseHandshake


class ClientHandshake(BaseHandshake):
    def __init__(self, resource_descriptor="/"):
        BaseHandshake.__init__(self)
        self.resource_descriptor = resource_descriptor


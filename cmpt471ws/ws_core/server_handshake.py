from cmpt471ws.ws_core.base_handshake import BaseHandshake
from cmpt471ws.ws_core.common import WebsocketCommon


class ServerHandshake(BaseHandshake):
    def __init__(self, http_status=404, http_status_message="uninitialized"):
        BaseHandshake.__init__(self)
        # TODO does http status has to be  short ? Move these to constants
        self.http_status = http_status
        self.http_status_message = http_status_message

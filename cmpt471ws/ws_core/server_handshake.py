from cmpt471ws.ws_core.base_handshake import BaseHandshake
from cmpt471ws.ws_core.common import WebsocketCommon


class ServerHandshake(BaseHandshake):
    def __init__(self):
        BaseHandshake.__init__(self)
        # TODO does http status has to be  short ? Move these to constants
        self.http_status = 200
        self.http_status_message = "SUCCEED"

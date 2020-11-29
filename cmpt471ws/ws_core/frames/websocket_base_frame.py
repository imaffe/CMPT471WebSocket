from cmpt471ws.ws_core.common import WebsocketCommon


class Frame():
    def __init__(self, op=WebsocketCommon.OP_CODE_TEXT):
        self.op = op
        self.fin = False
        self.rsv1 = False
        self.rsv2 = False
        self.rsv3 = False
        self.payload = None

    @classmethod
    def frame_factory_get(cls, op):
        return


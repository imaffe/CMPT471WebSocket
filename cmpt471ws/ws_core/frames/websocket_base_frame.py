from cmpt471ws.ws_core.common import WebsocketCommon


class Frame():
    def __init__(self, op=WebsocketCommon.OP_CODE_TEXT):
        self.op = op
        self.payload = None

    @classmethod
    def frame_factory_get(cls, op):
        return
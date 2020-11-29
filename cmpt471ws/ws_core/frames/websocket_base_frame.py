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
        if op == WebsocketCommon.OP_CODE_TEXT:
            return TextFrame()
        else:
            print("This frame is not supported yet, now returning")


class TextFrame(Frame):
    def __init__(self):
        Frame.__init__(self, WebsocketCommon.OP_CODE_TEXT)

    def is_valid(self):
        # TODO currently we don't add any validation code
        return True


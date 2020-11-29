from cmpt471ws.ws_core.common import WebsocketCommon
from cmpt471ws.ws_core.frames.websocket_base_frame import Frame


class TextFrame(Frame):
    def __init__(self):
        Frame.__init__(WebsocketCommon.OP_CODE_TEXT)

    def is_valid(self):
        # TODO currently we don't add any validation code
        return True

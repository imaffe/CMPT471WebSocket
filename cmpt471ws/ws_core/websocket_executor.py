from threading import Thread
import queue

from cmpt471ws.ws_core.websocket_impl import WebsocketImpl


class WebsocketWorker:
    def __init__(self):
        self.ws_impl_queue = queue.Queue()
        self.thread = Thread(target=self._poll_loop)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def _poll_loop(self):
        while True:
            ws_impl = self.ws_impl_queue.get(True, None)
            buf = ws_impl.get_inqueue()
            assert buf is not None
            # let the ws_impl to decode this data
            ws_impl.decode(bytearray(buf))

    def put_ws_queue(self, ws_impl: WebsocketImpl):
        self.ws_impl_queue.put(ws_impl)

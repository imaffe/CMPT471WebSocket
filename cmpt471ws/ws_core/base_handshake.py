

class BaseHandshake():
    def __init__(self):
        self.kvmap = {}
        self.content = bytearray()

    def put(self, key: str, value: str):
        self.kvmap[key] = value

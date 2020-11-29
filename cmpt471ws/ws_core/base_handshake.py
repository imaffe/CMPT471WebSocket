

class BaseHandshake():
    def __init__(self):
        self.kvmap = {}
        self.content = bytearray()

    def put(self, key: str, value: str):
        self.kvmap[key] = value

    def get(self, key):
        # return self.kvmap.get(key)
        return self.kvmap[key]



class BaseHandshake():
    def __init__(self):
        self.kvmap = {}

    def put(self, key: str, value: str):
        self.kvmap[key] = value

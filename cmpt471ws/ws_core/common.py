

class WebsocketCommon:
    DEFAULT_RCV_BUF_SIZE = 16384
    DEFAULT_PORT = 80

    # role enums
    ROLE_SERVER = "server"
    ROLE_CLIENT = "client"
    # connect state enums
    STATE_NOT_YET_CONNECTED = 100
    STATE_OPEN = 101
    STATE_CLOSING = 102
    STATE_CLOSED = 103

    # handshake state
    HANDSHAKE_STATE_MATCHED = 200

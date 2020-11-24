
# TODO put these field in a class
# some default values

DEFAULT_PORT = 80

# role enums
ROLE_SERVER = "server"
ROLE_CLIENT = "client"
# connect state enums
STATE_NOT_YET_CONNECTED = 100
STATE_OPEN = 101
STATE_CLOSING = 102
STATE_CLOSED = 103


class WebsocketCommon:
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

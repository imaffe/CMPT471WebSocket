import base64

from cmpt471ws.ws_core.client_handshake import ClientHandshake
from cmpt471ws.ws_core.common import WebsocketCommon
from cmpt471ws.ws_core.server_handshake import ServerHandshake
from cmpt471ws.ws_core.websocket_helper import WebsocketHelper


class WebsocketDraft:

    def __init__(self, role):
        self.role = role

    # handshake
    def translate_handshake(self, data):
        """
        return Handshake, could be ServerHandshake or ClientHandshake
        :param data:
        :return:
        """
        # TODO
        pass

    def create_handshake(self, handshake):
        """
        receive a Handshake object, could be ServerHandshake or ClientHandshak, and return a list of bytearray
        :param handshake:
        :return:
        """
        request_str = ""
        if isinstance(handshake, ClientHandshake):
            request_str = "GET " + handshake.resource_descriptor + " HTTP/1.1"
        elif isinstance(handshake, ServerHandshake):
            request_str = "HTTP/1.1 101 " + handshake.http_status_message
        else:
            print("Error invalid handshake type")


        request_str += "\r\n"

        # traverse through the headers
        for key, value in handshake.kvmap.items():
            request_str += key
            request_str += ": "
            request_str += value
            request_str += "\r\n"

        request_str += "\r\n"

        request_header_bytes = bytearray(request_str, "ascii")
        request_content_bytes = handshake.content

        request_all_bytes = request_header_bytes + request_content_bytes
        return [request_all_bytes]

    # server-only method
    def post_process_handshake_repsonse_as_server(self, handshake, response):
        # TODO
        pass

    # client-only method
    def post_process_handshake_request_as_client(self, handshake: ClientHandshake):
        # TODO put header fields
        handshake.put(WebsocketCommon.UPGRADE, "websocket")
        handshake.put(WebsocketCommon.CONNECTION, WebsocketCommon.UPGRADE)
        random_bytes = WebsocketHelper.random_bytearray(16)
        # TODO will this be transformed to base64 string ?
        random_base64_string = base64.b64encode(random_bytes).decode("ascii")
        handshake.put(WebsocketCommon.SEC_WEB_SOCKET_KEY, random_base64_string)
        handshake.put(WebsocketCommon.SEC_WEB_SOCKET_VERSION, "13")
        # TODO skip extensions for now
        # TODO skip protocols for now
        return handshake

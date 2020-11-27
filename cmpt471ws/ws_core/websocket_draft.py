import base64

from cmpt471ws.ws_core.base_handshake import BaseHandshake
from cmpt471ws.ws_core.client_handshake import ClientHandshake
from cmpt471ws.ws_core.common import WebsocketCommon
from cmpt471ws.ws_core.server_handshake import ServerHandshake
from cmpt471ws.ws_core.websocket_exceptions import WebsocketDecodeError
from cmpt471ws.ws_core.websocket_helper import WebsocketHelper


class WebsocketDraft:

    def __init__(self, role):
        self.role = role

    # handshake
    # TODO consider using exceptions to inform upper call stack
    # TODO or we can use enums to denote the status of the decode
    # TODO yeah how do we distinguish between a invalid handshake and a incomplete pakcet ?
    def translate_handshake(self, data):
        """
        return Handshake, could be ServerHandshake or ClientHandshake
        :param data:
        :return: None if the header is imcomplete,
        """
        return_data = data
        head_line, return_data = WebsocketHelper.read_string_line(return_data)
        if head_line is None:
            # do nothing and return None to indicate that this is a imcomplete header
            return None, data
        assert isinstance(head_line, str)
        first_line_tokens = head_line.split(' ', 3)
        if len(first_line_tokens) != 3:
            print("error parsing first line, invalid handshake")
            return WebsocketDecodeError("invalid header field"), data

        handshake = None
        if self.role == WebsocketCommon.ROLE_CLIENT:
            handshake = self._translate_handshake_client(first_line_tokens, head_line)
            assert isinstance(handshake, ServerHandshake)
        elif self.role == WebsocketCommon.ROLE_SERVER:
            handshake = self._translate_handshake_server(first_line_tokens, head_line)
            assert isinstance(handshake, ClientHandshake)
        else:
            print("error invalid role")

        # decode error
        if handshake is None or not isinstance(handshake, BaseHandshake):
            return WebsocketDecodeError("header line not match"), data

        key_value_line, return_data = WebsocketHelper.read_string_line(return_data)
        while key_value_line is not None and len(key_value_line) > 0:
            # None means incomplete, len == 0 means end of line
            pair = key_value_line.split(' ', 2)
            if len(pair) != 2:
                return WebsocketDecodeError("Invalid key value line"), data

            # TODO currently not support one key appear in multiple lines
            handshake.put(pair[0], pair[1])
            key_value_line, return_data = WebsocketHelper.read_string_line(return_data)

        # TODO should we keep it intact ?
        if key_value_line is None:
            # keep the data intact
            return None, data

        return handshake, return_data


    def _translate_handshake_client(self, first_line_tokens, head_line):
        pass


    # TODO can either return None or return a exception
    def _translate_handshake_server(self, first_line_token, head_line):
        if 'GET' != first_line_token[0]:
            print("Error header line first token is not GET")
            return None

        if 'HTTP/1.1' != first_line_token[2]:
            print("Error header line first token is not GET")
            return None

        resource_descriptor = first_line_token[1]
        return ClientHandshake(resource_descriptor)



    def accept_handshake_as_server(self, handshake):
        assert isinstance(handshake, ClientHandshake)

        version_str = handshake.get(WebsocketCommon.SEC_WEB_SOCKET_VERSION)
        version = int(version_str)
        if version != 13:
            return

        # TODO currently we ignore Extensions, Protocols and other stuffs


    def accept_handshake_as_client(self, handshake):
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

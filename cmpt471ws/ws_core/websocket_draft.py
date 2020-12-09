import base64
import datetime
import random

from cmpt471ws.ws_core.base_handshake import BaseHandshake
from cmpt471ws.ws_core.client_handshake import ClientHandshake
from cmpt471ws.ws_core.common import WebsocketCommon
from cmpt471ws.ws_core.frames.websocket_base_frame import Frame
from cmpt471ws.ws_core.frames.websocket_base_frame import TextFrame
from cmpt471ws.ws_core.server_handshake import ServerHandshake
from cmpt471ws.ws_core.websocket_exceptions import WebsocketDecodeError, WebsocketInvalidFrameError, WebsocketIncompletePacketError
from cmpt471ws.ws_core.websocket_helper import WebsocketHelper


class WebsocketDraft:

    def __init__(self, role):
        self.role = role
        self.imcomplete_frame = bytearray()

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
            # do nothing and raise WebsocketIncompletePacketError to indicate that this is a imcomplete header
            raise WebsocketIncompletePacketError('error translate_handshake: imcomplete header')
        assert isinstance(head_line, str)
        first_line_tokens = head_line.split(' ', 2)
        if len(first_line_tokens) != 3:
            print("error parsing first line, invalid handshake")
            raise WebsocketDecodeError("invalid header field")
        
        try:
            handshake = None
            if self.role == WebsocketCommon.ROLE_CLIENT:
                handshake = self._translate_handshake_client(first_line_tokens, head_line)
                assert handshake is None or isinstance(handshake, ServerHandshake)
            elif self.role == WebsocketCommon.ROLE_SERVER:
                handshake = self._translate_handshake_server(first_line_tokens, head_line)
                assert handshake is None or isinstance(handshake, ClientHandshake)
            else:
                raise ValueError("error invalid role")
        except WebsocketDecodeError as e:
            print("error header line not match")
            raise WebsocketDecodeError("header line not match")

        key_value_line, return_data = WebsocketHelper.read_string_line(return_data)
        while key_value_line is not None and len(key_value_line) > 0:
            # None means incomplete, len == 0 means end of line
            pair = key_value_line.split(':', 1)
            if len(pair) != 2:
                raise WebsocketDecodeError("Invalid key value line")

            # TODO currently not support one key appear in multiple lines
            print("WS_DRAFT: putting key value while translating handshake {}, {}".format(pair[0], pair[1]))
            handshake.put(pair[0].strip(), pair[1].strip())
            key_value_line, return_data = WebsocketHelper.read_string_line(return_data)

        # TODO should we keep it intact ?
        if key_value_line is None:
            # keep the data intact
            return None, data

        return handshake, return_data

    def _translate_handshake_client(self, first_line_token, head_line):
        if '101' != first_line_token[1]:
            print("Error header line second token is not 101")
            return None

        if 'HTTP/1.1' != first_line_token[0]:
            print("Error header line first token is not HTTP")
            return None

        http_status = 101
        http_status_message = first_line_token[2]
        return ServerHandshake(http_status, http_status_message)

    # can raise a exception
    def _translate_handshake_server(self, first_line_token, head_line):
        if 'GET' != first_line_token[0]:
            raise WebsocketDecodeError("Error header line first token is not GET, instead it is:{}".format(first_line_token[0]))

        if 'HTTP/1.1' != first_line_token[2]:
            raise WebsocketDecodeError("Error header line first token is not HTTP/1.1, instead it is:{}".format(first_line_token[0]))

        resource_descriptor = first_line_token[1]
        return ClientHandshake(resource_descriptor)

    def translate_frames(self, data):
        assert isinstance(data, bytearray)
        assert len(data) > 0

        frames = []
        while True:
            if len(self.imcomplete_frame) > 0:
                # finish what is left
                self.imcomplete_frame.extend(data)
                data = self.imcomplete_frame

            while len(data) > 0:
                frame, data = self._translate_single_frame(data)
                if frame is None:
                    # means incomplete frame
                    self.imcomplete_frame = data
                    return frames
                else:
                    frames.append(frame)

            return frames

    def _translate_single_frame(self, data):
        return_data = data.copy()
        assert isinstance(return_data, bytearray)
        data_len = len(data)
        real_packet_size = 2
        if data_len < real_packet_size:
            # Imcomplete data
            return None, data
        # TODO we don't put any size constraints on frames
        b1 = return_data[0]
        print("WS_DRAFT: first byte is {0:b} {1}".format(b1, b1))
        fin = b1 >> 8 != 0
        rsv1 = (b1 & 0x40) != 0
        rsv2 = (b1 & 0x20) != 0
        rsv3 = (b1 & 0x10) != 0

        b2 = return_data[1]
        print("WS_DRAFT: second byte is {0:b} {1}".format(b2, b2))
        mask = (b2 & -128) != 0
        # TODO will this actually work ?
        payloadlength = b2 & ~128
        # payloadlength = b2 & 127
        opcode = self._to_opcode(b1 & 15)
        print("WS_DRAFT: payload length is {0:b} {1}".format(payloadlength, payloadlength))
        print("WS_DRAFT: opcode is {0:b} {1}".format(b1 & 15, b1 & 15))

        return_data = return_data[2:]
        if payloadlength < 0 or payloadlength > 125:
            # TODO the first two bits should not be passed in

            print("after truncate the first 2 bytes : {}".format(WebsocketHelper.bytearray_to_ascii_string(return_data)))
            try:
                payloadlength, real_packet_size, return_data = self._translate_single_frame_for_real_length(
                    return_data,
                    opcode,
                    payloadlength,
                    data_len,
                    real_packet_size
                )
            except WebsocketInvalidFrameError as e:
                raise e
            
        if data_len < real_packet_size:
            # Imcomplete data
            return None, data

        real_packet_size += 4 if mask else 0
        real_packet_size += payloadlength

        payload = bytearray
        if data_len < real_packet_size:
            # Imcomplete data
            return None, data

        if mask:
            # TODO give this to Sam or Ruikai
            mask_key = return_data[:4]
            return_data = return_data[4:]
            payload = bytearray()
            for i in range(payloadlength):
                payload.extend(WebsocketHelper.int_to_bytes_for_size(return_data[i] ^ mask_key[i%4],4))
            return_data = return_data[payloadlength:]
        else:
            payload = return_data[:payloadlength]
            return_data = return_data[payloadlength:]

        frame = Frame.frame_factory_get(opcode)
        frame.fin = fin
        frame.rsv1 = rsv1
        frame.rsv2 = rsv2
        frame.rsv3 = rsv3
        # TODO skip extension and protocol validation
        frame.payload = payload

        # TODO which will it use ?
        is_valid = frame.is_valid()

        if is_valid:
            print("after decode the bytes left are {}".format(len(return_data)))
            return frame, return_data
        else:
            raise WebsocketInvalidFrameError("Invalid frame", data)

        # self._check_payload_limit(payloadlength)


    def _translate_single_frame_for_real_length(self,
                data,
                opcode,
                oldpayloadlength,
                data_len,
                old_real_packet_size
            ):
        """
        returns the real payload length and real packet size plus the modified data
        """
        return_data = data.copy()
        payloadlength = oldpayloadlength
        real_packet_size = old_real_packet_size
        if opcode == WebsocketCommon.PING or opcode == WebsocketCommon.OP_CODE_PONG or opcode == WebsocketCommon.OP_CODE_CLOSING:
            raise WebsocketInvalidFrameError("Some frames cannot have longer payload length", data)


        if payloadlength == 126:
            real_packet_size += 2
            size_bytearray = bytearray()
            size_bytearray.append(0)
            size_bytearray.append(return_data[0])
            size_bytearray.append(return_data[1])
            return_data = return_data[2:]
            payloadlength = WebsocketHelper.bytes_to_int(size_bytearray)
        else:
            real_packet_size += 8
            size_bytearray = bytearray()
            for i in range(8):
                size_bytearray.append(return_data[i])
            return_data = return_data[8:]
            payloadlength = WebsocketHelper.bytes_to_int(size_bytearray)

        return payloadlength, real_packet_size, return_data

    def _to_opcode(self, n):
        if n == 0:
            return WebsocketCommon.OP_CODE_CONTINUOUS
        elif n == 1:
            return WebsocketCommon.OP_CODE_TEXT
        elif n == 2:
            return WebsocketCommon.OP_CODE_BINARY
        elif n == 8:
            return WebsocketCommon.OP_CODE_CLOSING
        elif n == 9:
            return WebsocketCommon.OP_CODE_PING
        elif n == 10:
            return WebsocketCommon.OP_CODE_PONG
        else:
            raise ValueError("Error opcode invalid")

    def process_frame(self, ws_impl, frame):
        if frame.op == WebsocketCommon.OP_CODE_CLOSING:
            # TODO Sam or Ruikai
            pass
        elif frame.op == WebsocketCommon.OP_CODE_PONG:
            pass
        elif frame.op == WebsocketCommon.OP_CODE_PING:
            pass
        elif frame.op == WebsocketCommon.OP_CODE_CONTINUOUS:
            pass
        elif frame.op == WebsocketCommon.OP_CODE_TEXT:
            # TODO can add some error protection code
            assert isinstance(frame.payload, bytearray)
            # TODO notice we use UTF-8 encoding here
            message = frame.payload.decode('utf-8')
            ws_impl.listener.on_websocket_message(ws_impl, message)
        elif frame.op == WebsocketCommon.OP_CODE_BINARY:
            # TODO currently we don't support binary interfaces exposed, so all binary is passed as
            assert isinstance(frame.payload, bytearray)
            base64_message = base64.b64encode(frame.payload).decode('ascii')
            ws_impl.listener.on_websocket_message(ws_impl, base64_message)
        else:
            raise ValueError("Error, invalid opcode while processing the frames")

        return True

    def accept_handshake_as_server(self, handshake):
        assert isinstance(handshake, ClientHandshake)

        version_str = handshake.get(WebsocketCommon.SEC_WEB_SOCKET_VERSION)
        version = int(version_str)
        if version != 13:
            return WebsocketCommon.HANDSHAKE_STATE_NOT_MATCHED
        else:
            return WebsocketCommon.HANDSHAKE_STATE_MATCHED
        # TODO currently we ignore Extensions, Protocols and other stuffs

    def accept_handshake_as_client(self, request, response):

        assert isinstance(response, ServerHandshake)
        if response.get(WebsocketCommon.UPGRADE) != 'websocket' or str(response.get(WebsocketCommon.CONNECTION)).lower().find(
                'upgrade') == -1:
            print("WS_DRAFT: missing upgrade or connection")
            return WebsocketCommon.HANDSHAKE_STATE_NOT_MATCHED

        # TODO why do we need to verify if client handshake ?
        if response.get(WebsocketCommon.SEC_WEB_SOCKET_ACCEPT) is None:
            print("WS_DRAFT: missing SEC_WEB_SOCKET_ACCEPT")
            return WebsocketCommon.HANDSHAKE_STATE_NOT_MATCHED

        if request.get(WebsocketCommon.SEC_WEB_SOCKET_KEY) is None:
            print("WS_DRAFT: missing SEC_WEB_SOCKET_KEY")
            return WebsocketCommon.HANDSHAKE_STATE_NOT_MATCHED

        sec_key = request.get(WebsocketCommon.SEC_WEB_SOCKET_KEY)
        sec_answer = response.get(WebsocketCommon.SEC_WEB_SOCKET_ACCEPT)
        our_answer = self._generate_final_key(sec_key)

        if our_answer != sec_answer:
            print("Error client key not match")
            return WebsocketCommon.HANDSHAKE_STATE_NOT_MATCHED

        # TODO ignore extensions and protocols
        return WebsocketCommon.HANDSHAKE_STATE_MATCHED

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


    def create_text_frames(self, message):
        """
        Currently only supports string type message
        :param message:
        :return:
        """
        assert isinstance(message, str)

        text_frame = TextFrame()
        text_frame.payload = WebsocketHelper.str_to_utf8_bytearray(message)
        return [text_frame]

    def create_binary_frames(self, data):
        assert isinstance(data, bytearray)
        # TODO don't support binary frames for now


    def create_bytearray_for_frame(self, frame):
        assert isinstance(frame, Frame)

        payload = frame.payload
        result = bytearray()
        # TODO wait mask is a must support for Client
        # TODO give mask support to Sam or Ruikai
        # mask = self.role == WebsocketCommon.ROLE_CLIENT
        mask = False
        size_bytes = self._get_size_bytes(payload)
        opt_code = frame.op
        one_int8 = -128 if frame.fin else 0

        one = opt_code | one_int8

        if frame.rsv1:
            one = one | self._get_rsv_byte(1)

        if frame.rsv2:
            one = one | self._get_rsv_byte(2)

        if frame.rsv3:
            one = one | self._get_rsv_byte(3)

        # add the first bytes
        one_bytes = WebsocketHelper.int8_to_bytes(one)
        result.extend(one_bytes)
        # calculate the second bytes
        payload_length = len(frame.payload)
        payload_length_bytearray = WebsocketHelper.int_to_bytes_for_size(payload_length, size_bytes)
        assert len(payload_length_bytearray) == size_bytes

        if size_bytes == 1:
            length_plus_mask = payload_length | self._get_mask_int(mask)
            length_plus_mask_bytes = WebsocketHelper.int8_to_bytes(length_plus_mask)
            result.extend(length_plus_mask_bytes)
        elif size_bytes == 2:
            length_plus_mask = 126 | self._get_mask_int(mask)
            length_plus_mask_bytes = WebsocketHelper.int8_to_bytes(length_plus_mask)
            result.extend(length_plus_mask_bytes)
            result.extend(payload_length_bytearray)
        elif size_bytes == 8:
            length_plus_mask = 127 | self._get_mask_int(mask)
            length_plus_mask_bytes = WebsocketHelper.int8_to_bytes(length_plus_mask)
            result.extend(length_plus_mask_bytes)
            result.extend(payload_length_bytearray)
        else:
            print("Error impossible these many bytes")

        if mask:
            # TODO implemented by Ruikai and Sam
            mask_key = bytearray()
            mask_key.extend(WebsocketHelper.int_to_bytes_for_size(random.randint(-pow(2, 31), pow(2,31)-1), 4))
            result.extend(mask_key)
            i = 0
            for i in range(len(payload)):
                result.extend(WebsocketHelper.int_to_bytes_for_size((payload[i] ^ mask_key[(i % 4)]), 4))
        else:
            result.extend(payload)

        return result

    def _get_mask_int(self, mask):
        return -128 if mask else 0


    def _get_rsv_byte(self, rsv):
        if rsv == 1:
            return 0x40
        elif rsv == 2:
            return 0x20
        elif rsv == 3:
            return 0x20
        else:
            return 0

    def _get_size_bytes(self, payload):
        length = len(payload)
        if length <= 125:
            return 1
        elif length <= 65535:
            return 2
        else:
            return 8


    # server-only method
    def post_process_handshake_repsonse_as_server(self, request, response):
        assert isinstance(request, ClientHandshake)
        assert isinstance(response, ServerHandshake)
        response.put(WebsocketCommon.UPGRADE, 'websocket')
        response.put(WebsocketCommon.CONNECTION, request.get(WebsocketCommon.CONNECTION))
        sec_key = request.get(WebsocketCommon.SEC_WEB_SOCKET_KEY)
        # TODO what could the sec_key be here ?
        if sec_key is None or sec_key == '':
            raise WebsocketDecodeError("Invalid handshake")
        assert isinstance(sec_key, str)
        response.put(WebsocketCommon.SEC_WEB_SOCKET_ACCEPT, self._generate_final_key(sec_key))

        # TODO ignore protocols and extensions

        response.http_status_message = "Web Socket Protocol Handshake"
        response.put("Server", "CMPT471 Python-WebSocket")
        response.put("Date", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        return response

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

    def _generate_final_key(self, sec_key):
        assert isinstance(sec_key, str)
        final_key = sec_key.strip() + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        # TODO still not complete

        # 1. sha1
        # 2. encode
        return final_key

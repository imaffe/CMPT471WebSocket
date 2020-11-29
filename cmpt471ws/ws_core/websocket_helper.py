import os
import socket

from cmpt471ws.ws_core.common import WebsocketCommon


class WebsocketHelper:

    def __init__(self):
        pass

    @classmethod
    def batch(cls, ws_impl):
        # TODO
        pass

    @classmethod
    def read(cls, ws_impl, sock: socket.socket):
        # TODO this should always be non-blocking
        data = sock.recv(WebsocketCommon.DEFAULT_RCV_BUF_SIZE)
        if not data:
            pass
            # TODO we should log something here

        return data

    @classmethod
    def random_bytearray(cls, size: int):
        return bytearray(os.urandom(size))

    @classmethod
    def read_string_line(cls, data: bytearray):
        """
        get a line from the data, if not a line return None
        TODO we still need to be clear about what this method returns
        :param data:
        :return: None if no line endings found, empty string if there is line ending
        """
        assert isinstance(data, bytearray)
        headline, data = cls.read_line(data)
        if headline is not None:
            return str(headline), data
        else:
            return headline, data


    @classmethod
    def read_line(cls, data: bytearray):
        """
        in python, iterate a bytearray gives the integer representation 0~255 of each byte
        ord() gives the bytes representation of a given array using unicode. Since unicode
        is compatible with ascii, so it is ok for us to use unicode encoding.
        Notice this method might change the content of the input bytearray
        :param data:
        :return: a bytearray without trailing line ending, and a new remaining bytearray
        """
        assert isinstance(data, bytearray)
        prev = '0'
        cur = '0'
        for index, b in enumerate(data):
            prev = cur
            cur = b
            if cur == ord('\n') and prev == ord('\r'):
                line = data[:index - 1]
                data_remain = data[index + 1:]
                return line, data_remain

        # if no line endings appears, return None
        return None, data


    @classmethod
    def str_to_ascii_bytearray(cls, s):
        assert s is not None
        assert isinstance(s, str)
        return bytearray(s.encode('ascii'))

    @classmethod
    def str_to_utf8_bytearray(cls, s):
        assert s is not None
        assert isinstance(s, str)
        return bytearray(s.encode('utf-8'))

    @classmethod
    def ascii_bytearray(cls, data):
        assert data is not None
        assert isinstance(data, bytearray)
        return data.decode('ascii')


    # All bytes int conversion should be using these methods

    @classmethod
    def int8_to_bytes(cls, n):
        assert isinstance(n, int) and n >= -128 and n <= 127
        return n.to_bytes(1, byteorder='big', signed=True)

    @classmethod
    def bytes_to_int(cls, data):
        assert isinstance(data, bytearray)
        return int.from_bytes(data, byteorder='big', signed=True)

    @classmethod
    def int_to_bytes_for_size(cls, n, size):
        assert isinstance(n, int)
        return n.to_bytes(size, byteorder='big', signed=True)

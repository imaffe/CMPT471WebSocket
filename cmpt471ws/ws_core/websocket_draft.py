
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
        # TODO
        pass
    # server-only method
    def post_process_handshake_repsonse_as_server(self, handshake, response):
        # TODO
        pass



    # client-only method

    def post_process_handshake_request_as_client(self, handshake, response):
        # TODO
        pass

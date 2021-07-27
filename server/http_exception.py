from . import http_responses

class HTTPException(Exception):
    def __init__(self, code, message):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    @property
    def code_and_message(self):
        return "%s %s" % str(self._code), self._message

    @property
    def code_description_and_message(self):
        _, http_msg = http_responses.get_http_response_info(self._code)
        return "%s %s. %s" % (str(self._code), http_msg, self._message)



class Response:
    """
    Universal website response
    """

    def __init__(self, status_code, content, headers) -> None:
        self._status_code = status_code
        self._content = content
        self._headers = headers


    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def content(self) -> bytes:
        return self._content

    @property
    def headers(self) -> dict:
        return self._headers
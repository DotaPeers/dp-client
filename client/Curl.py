import pycurl
from urllib.parse import urlencode
from io import BytesIO


class Curl:

    def __init__(self, url):
        self._url = url
        self._c = pycurl.Curl()
        self._buffer = BytesIO()

    def connect(self):
        self._c.setopt(self._c.URL, self._url)
        self._c.setopt(self._c.WRITEDATA, self._buffer)
        self._c.perform()

    def disconnect(self):
        self._c.close()

    def write(self, data):
        self._buffer.truncate(0)
        self._buffer.seek(0)
        self._c.setopt(self._c.POSTFIELDS, urlencode(data))
        self._c.perform()

        return self._buffer.getvalue()

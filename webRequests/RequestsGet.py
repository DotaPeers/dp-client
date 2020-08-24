import requests
from webRequests.Response import Response


class RequestsGet:
    """
    Gets the content of a page using requests.
    Returns the data in the unified format Response
    """

    @staticmethod
    def get(url) -> Response:
        r = requests.get(url)

        return Response(r.status_code, r.content, dict(r.headers))

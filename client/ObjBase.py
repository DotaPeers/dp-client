import json, time

from webRequests.RequestsGet import RequestsGet
import Config


class ObjBase(object):
    """
    Base Class for API objects
    """

    def _loadData(self, url):
        if Config.USE_NGINX:
            url = 'http://localhost:3214/api/{}'.format(url)
        else:
            url = 'https://api.opendota.com/api/{}'.format(url)
        r = RequestsGet.get(url)

        if r.status_code != 200:
            raise Exception('Request {} returned status code {}.'.format(url, r.status_code))

        # Handle the request timeouts
        isFromCache = r.headers.get('X-Proxy-Cache', 'UNKNOWN')
        limitMin = int(r.headers.get('X-Rate-Limit-Remaining-Minute', '-1'))
        limitMonth = int(r.headers.get('X-Rate-Limit-Remaining-Month', '-1'))

        # Check if the data if from the cache
        if isFromCache == 'UNKNOWN':
            print('[Error] Request {} has no information about the cache status.'.format(url))

        # Important: Only evaluate the rate limits if the data is not from the cache.
        # If it comes from the cache, the rate limitation is irrelevant
        if isFromCache != 'HIT':
            # Check the minutely limit
            if limitMin == -1:
                print('[Error] No minutely rate limit found for {}.'.format(url))

            if limitMin <=3:
                print('Exceded rate limit. Waiting 30s.')
                time.sleep(30)

            # Check the monthly limit
            if limitMonth == -1:
                print('[Error] No monthly rate limit found for {}.'.format(url))

            if limitMonth <= 100:
                print('[Fatal Error] Monthly rate limit exceeded.')
                exit(-10)

        return json.loads(r.content.decode())

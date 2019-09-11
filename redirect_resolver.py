#!/bin/python3
import urllib.request

class RedirectResolver:

    def __init__(self, max_redirects=3):
        self._max_redirects = max_redirects

    def resolve(self, url):
        opener = urllib.request.build_opener(
            _RedirectHandler(url, self._max_redirects))
        with opener.open(url) as http_response:
            return http_response.geturl()

class TooManyRedirectsError(Exception):
    pass

class CyclicRedirectError(Exception):
    pass

class _RedirectHandler(urllib.request.HTTPRedirectHandler):

    def __init__(self, url, max_redirects):
        self._max_redirects = max_redirects
        self._redirect_counter = 0
        self._visited = set([url])
        super().__init__()

    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        '''
            That function reimplements features of HTTPRedirectHandler
            for loop detection since interface for controlling detection
            behavious isn't documented and could be treated as private
        '''
        self._redirect_counter += 1
        if self._redirect_counter > self._max_redirects:
            raise TooManyRedirectsError()
        if newurl in self._visited:
            raise CyclicRedirectError()
        self._visited.add(newurl)
        return super().redirect_request(req, fp, code, msg, hdrs, newurl)

if __name__ == '__main__':
    print('hello')

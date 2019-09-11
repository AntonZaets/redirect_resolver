#!/bin/python3
import urllib.request

class RedirectResolver:

    def __init__(self, max_redirects=3):
        self._max_redirects = max_redirects

    def resolve(self, url):
        opener = urllib.request.build_opener(
            _RedirectHandler(self._max_redirects))
        with opener.open(url) as http_response:
            print('GET {} - url: {} info: {} code {}'.format(
                url,
                http_response.geturl(),
                http_response.info(),
                http_response.getcode()))
            return http_response.geturl()

class TooManyRedirectsError(Exception):
    pass

class CyclicRedirectError(Exception):
    pass

class _RedirectHandler(urllib.request.HTTPRedirectHandler):

    def __init__(self, max_redirects):
        self._max_redirects = max_redirects
        self._redirect_counter = 0

    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        self._redirect_counter += 1
        if self._redirect_counter > self._max_redirects:
            raise TooManyRedirectsError()
        return super().redirect_request(req, fp, code, msg, hdrs, newurl)

if __name__ == '__main__':
    print('hello')

#!/bin/python3
from urllib import request

class RedirectResolver:

    def __init__(self, max_redirects=3):
        pass

    def resolve(self, url):
        with request.urlopen(url) as http_response:
            print('GET {} - url: {} info: {} code {}'.format(
                url,
                http_response.geturl(),
                http_response.info(),
                http_response.getcode()))
            return http_response.geturl()

if __name__ == '__main__':
    print('hello')

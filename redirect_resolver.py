#!/bin/python3
"""Module and application for finding the target url in chain of redirects"""

import argparse
import urllib.request


class RedirectResolver:
    """The class that delivers functionality for url resolving"""

    def __init__(self, max_redirects=3, ignore_unlimited=False):
        """
            :param max_redirects: maximum number of redirects before
                                  rising TooManyRedirectsError
            :param ignore_unlimited: don't rise UnlimitedContentError if
                                     chunked response is detected
        """
        self._max_redirects = max_redirects
        self._ignore_unlimited = ignore_unlimited

    def resolve(self, url):
        """finds a target url in the chain of redirects for url"""
        handlers = [_RedirectHandler(url, self._max_redirects)]
        if not self._ignore_unlimited:
            handlers.append(_UnlimitedContentProcessor())
        opener = urllib.request.build_opener(*handlers)
        request = urllib.request.Request(url, method='HEAD')
        with opener.open(request) as http_response:
            return http_response.geturl()


class TooManyRedirectsError(Exception):
    """It's raised if too many redirects occured for url"""
    pass


class CyclicRedirectError(Exception):
    """It's raised if the cycle is detected for url"""
    pass


class UnlimitedContentError(Exception):
    """It's raised if the chunked response is detected"""
    pass


class _RedirectHandler(urllib.request.HTTPRedirectHandler):
    """Overrided handler for redirections"""

    def __init__(self, url, max_redirects):
        """
            :param url: url for resolving
            :param max_redirects: maximum number of redirects
                                  during resolving of the url
        """
        self._max_redirects = max_redirects
        self._redirect_counter = 0
        self._visited = set([url])
        super().__init__()

    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        """
            That function reimplements features of HTTPRedirectHandler
            for loop detection due too several reasons:
                - interface for controlling detection behaviour isn't
                  documented and variables for controlling that are stored
                  as static members of HTTPRedirectHandler;
                - support for continue with  'HEAD' after redirection
        """
        self._redirect_counter += 1
        if self._redirect_counter > self._max_redirects:
            raise TooManyRedirectsError()
        if newurl in self._visited:
            raise CyclicRedirectError()
        self._visited.add(newurl)
        new_request = super().redirect_request(
            req, fp, code, msg, hdrs, newurl)
        new_request.method = 'HEAD'
        return new_request

    def http_error_308(self, req, fp, code, msg, hdrs):
        """Method for supporting the redirection after getting
           the 308 from the server
        """
        return super().http_error_307(req, fp, 307, msg, hdrs)


class _UnlimitedContentProcessor(urllib.request.HTTPErrorProcessor):

    def __init__(self):
        super().__init__()

    def http_response(self, req, resp):
        """Method raises if response is 'chunked'
        """
        transfer_value = resp.getheader('transfer-encoding')
        if transfer_value and 'chunked' in transfer_value:
            raise UnlimitedContentError()
        return super().http_response(req, resp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-redirects', type=int, default=5,
                        help='Maximum number of redirects')
    parser.add_argument('--ignore-unlimited-content',
                        action='store_true', default=False,
                        help='''Don\'t rise an exception if content
                                    may have unlimited size''')
    parser.add_argument('url', type=str, help='URL for resolving')
    args = parser.parse_args()
    resolver = RedirectResolver(
        max_redirects=args.max_redirects,
        ignore_unlimited=args.ignore_unlimited_content)
    print(resolver.resolve(args.url))

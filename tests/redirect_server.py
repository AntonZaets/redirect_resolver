import itertools
import uuid
from urllib.parse import urljoin
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread


class RedirectServer(HTTPServer):
    """Server for testing the RedirectResolver"""

    def __init__(self):
        super().__init__(('127.0.0.1', 8080), _RedirectRequestHandler)
        self._thread = Thread(target=self.serve_forever)
        # that variable maps paths to generators of a new paths, codes
        # and headers
        self._redirects = {}

    def start(self):
        self._thread.start()

    def stop(self):
        self.shutdown()
        self._thread.join()

    def many_redirects(self, code, num):
        """Creates a multiple redirect
            :param code: response code for redirect (30x)
            :param num: number of redirects (more than 0)
            :return: tuple like (url_for_resolving, expected_url)
        """
        assert code in self.get_redirect_codes()
        assert num > 0, "number of redirects should be greater than 0"
        path = self._random_path()
        target_path = self._random_path()
        self._redirects[path] = self._make_many_redirects_gen(
            path, target_path, code, num)
        return (self._build_url(path), self._build_url(target_path))

    def cyclic_redirect(self, code, num):
        """Creates a cyclic redirect
            :param code: response code for redirect (30x)
            :param num: number of redirects (more than 0)
            :return: url for resolving
        """
        assert code in self.get_redirect_codes()
        assert num > 0, "number of redirects should be greater than 0"
        path = self._random_path()
        self._redirects[path] = self._make_cycle_redirects_gen(path, code, num)
        return self._build_url(path)

    def no_redirects(self):
        """Create url without any redirect"""
        path = self._random_path()
        self._redirects[path] = itertools.cycle([(200, [])])
        return self._build_url(path)

    def unlimited_content(self):
        """Create url with chunked response"""
        path = self._random_path()
        chunked_headers = [('Transfer-Encoding', 'gzip, chunked')]
        self._redirects[path] = itertools.cycle([(200, chunked_headers)])
        return self._build_url(path)

    def get_redirect_info(self, path):
        """
            :return: information about redirect for path,
                     tuple like (response_code, list_of_headers)
        """
        assert path in self._redirects,\
            'path {} not in {}'.format(path, self._redirects.keys())
        try:
            return next(self._redirects[path])
        except StopIteration:
            return (200, [])

    @staticmethod
    def get_redirect_codes():
        """HTTP codes that should be trated as redirection"""
        return [301, 302, 303, 307, 308]

    def _make_many_redirects_gen(self, init_path, target_path, code, num):
        previous_path = init_path
        paths = [(code, self._random_path()) for i in range(0, num - 1)] \
            + [(code, target_path)]
        for new_code, new_path in paths:
            generator = self._redirects[previous_path]
            # unregister/register generator for a old/new path
            del self._redirects[previous_path]
            self._redirects[new_path] = generator
            previous_path = new_path

            yield (new_code, [('Location', self._build_url(new_path))])

    def _make_cycle_redirects_gen(self, init_path, code, num):
        paths = [self._random_path() for i in range(0, num - 1)] \
              + [init_path]
        previous_path = init_path
        for new_path in itertools.cycle(paths):
            generator = self._redirects[previous_path]
            # unregister/register generator for a old/new path
            del self._redirects[previous_path]
            self._redirects[new_path] = generator
            previous_path = new_path
            yield (code, [('Location', self._build_url(new_path))])

    def _random_path(self):
        return '/{}'.format(uuid.uuid4().hex)

    def _build_url(self, path):
        address, port = self.server_address
        return urljoin('http://{}:{}/'.format(address, port), path)


class _RedirectRequestHandler(BaseHTTPRequestHandler):
    """Class implements response for HEAD request with
       optional redirects"""
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_HEAD(self):
        basic_headers = [('Content-Length', '0')]
        response_code, path_specific_headers = \
            self.server.get_redirect_info(self.path)
        headers_dict = dict(basic_headers + path_specific_headers)
        self.send_response(response_code, '')
        for header_name, header_value in headers_dict.items():
            self.send_header(header_name, header_value)
        self.end_headers()

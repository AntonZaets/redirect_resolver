import itertools
import uuid
from urllib.parse import urljoin
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

class RedirectServer(HTTPServer):

    def __init__(self):
        super().__init__(('127.0.0.1', 8080), RedirectRequestHandler)
        self._thread = Thread(target=self.serve_forever)
        self._redirects = {}

    def start(self):
        self._thread.start()

    def stop(self):
        self.shutdown()
        self._thread.join()

    def many_redirects(self, code, num):
        assert num > 0, "number of redirects should be greater than 0"
        path = self._random_path()
        target_path = self._random_path()
        print('generator of many redirects for path {}'.format(path))
        self._redirects[path] = self._gen_many_redirects(
            path, target_path, code, num)
        return (self._build_url(path), self._build_url(target_path))

    def cyclic_redirect(self, code, num):
        assert num > 0, "number of redirects should be greater than 0"
        path = self._random_path()
        print('generator of cyclic redirects for path {}'.format(path))
        self._redirects[path] = self._gen_cycle_redirects(path, code, num)
        return self._build_url(path)

    def no_redirects(self):
        path = self._random_path()
        self._redirects[path] = itertools.cycle([(200, [])])
        return self._build_url(path)

    def unlimited_content(self):
        path = self._random_path()
        chunked_headers = [('Transfer-Encoding', 'gzip, chunked')]
        self._redirects[path] = itertools.cycle([(200, chunked_headers)])
        return self._build_url(path)

    def get_redirect_info(self, path):
        #it's better to explicitly crash for unexpected path,
        #since RedirectServer is used for testing purpose
        assert path in self._redirects, \
               'path {} not in {}'.format(path, self._redirects.keys())
        try:
            return next(self._redirects[path])
        except StopIteration:
            return (200, [])

    @staticmethod
    def get_redirect_codes():
        return [301, 302, 303, 307, 308]

    def _gen_many_redirects(self, init_path, target_path, code, num):
        previous_path = init_path
        paths = [(code, self._random_path()) for i in range(0, num - 1)] \
              + [(code, target_path)]
        for new_code, new_path in paths:
            generator = self._redirects[previous_path]
            del self._redirects[previous_path]
            self._redirects[new_path] = generator
            previous_path = new_path
            yield (new_code, [('Location', self._build_url(new_path))])

    def _gen_cycle_redirects(self, init_path, code, num):
        paths = [self._random_path() for i in range(0, num - 1)] \
              + [init_path]
        previous_path = init_path
        for new_path in itertools.cycle(paths):
            generator = self._redirects[previous_path]
            del self._redirects[previous_path]
            self._redirects[new_path] = generator
            previous_path = new_path
            yield (code, [('Location', self._build_url(new_path))])

    def _random_path(self):
        return '/{}'.format(uuid.uuid4().hex)

    def _build_url(self, path):
        address, port = self.server_address
        return urljoin('http://{}:{}/'.format(address, port), path)

class RedirectRequestHandler(BaseHTTPRequestHandler):
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

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

    def many_redirects(self, num):
        assert num > 0, "number of redirects should be greater than 0"
        path = self._random_path()
        target_path = self._random_path()
        print('generator of many redirects for path {}'.format(path))
        self._redirects[path] = self._gen_many_redirects(path, target_path, num)
        return (self._build_url(path), self._build_url(target_path))

    def cyclic_redirect(self, num):
        assert num > 0, "number of redirects should be greater than 0"
        path = self._random_path()
        print('generator of cyclic redirects for path {}'.format(path))
        self._redirects[path] = self._gen_cycle_redirects(path, num)
        return self._build_url(path)

    def no_redirects(self):
        path = self._random_path()
        self._redirects[path] = itertools.cycle([])
        return self._build_url(path)

    def do_redirect(self, path):
        #it's better to explicitly crash for unexpected path,
        #since RedirectServer is used for testing purpose
        assert path in self._redirects, \
               'path {} not in {}'.format(path, self._redirects.keys())
        try:
            return self._build_url(next(self._redirects[path]))
        except StopIteration:
            return None

    def get_redirect_codes(self):
        return [301, 302, 303, 307, 308]

    def _gen_many_redirects(self, init_path, target_path, num):
        previous_path = init_path
        paths = [self._random_path() for i in range(0, num - 1)] \
              + [target_path]
        for new_path in paths:
            generator = self._redirects[previous_path]
            del self._redirects[previous_path]
            self._redirects[new_path] = generator
            previous_path = new_path
            yield new_path

    def _gen_cycle_redirects(self, init_path, num):
        paths = [self._random_path() for i in range(0, num - 1)] \
              + [init_path]
        previous_path = init_path
        for new_path in itertools.cycle(paths):
            generator = self._redirects[previous_path]
            del self._redirects[previous_path]
            self._redirects[new_path] = generator
            previous_path = new_path
            yield new_path

    def _random_path(self):
        return '/{}'.format(uuid.uuid4().hex)

    def _build_url(self, path):
        address, port = self.server_address
        return urljoin('http://{}:{}/'.format(address, port), path)

class RedirectRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_HEAD(self):
        location = self.server.do_redirect(self.path)
        response_code = self.server.get_redirect_codes()[0] if location \
                        else 200
        self.send_response(response_code, '')
        self.send_header('Content-Length', '0')
        if location:
            self.send_header('Location', location)
        self.end_headers()
        self.log_message('Response: %d. Location: %s', response_code, location)

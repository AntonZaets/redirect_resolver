from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

class RedirectServer:

    def __init__(self):
        self.__server = HTTPServer(('127.0.0.1', 8080), RedirectRequestHandler())
        self.__thread = Thread(target=self.__server.serve_forever)

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__server.shutdown()
        self.__thread.join()

    def many_redirects(self, num):
        pass

    def cyclic_redirect(self):
        pass

class RedirectRequestHandler:
    def __init__(self):
        pass

    def do_GET(self):
        print(self.path)

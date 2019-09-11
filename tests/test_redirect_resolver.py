import pytest

from redirect_resolver import RedirectResolver
from redirect_server import RedirectServer

@pytest.fixture(scope='module')
def server():
    server = RedirectServer()
    server.start()
    yield server
    server.stop()

def test_no_redirects(server):
    resolver = RedirectResolver()
    url_without_redirects = server.no_redirects()
    assert resolver.resolve(url_without_redirects) == url_without_redirects

def test_many_redirects(server):
    redirects_num = 3
    resolver = RedirectResolver()
    assert resolver.resolve(server.many_redirects(redirects_num)) == None

def test_too_many_redirects(server):
    max_redirects = 1
    resolver = RedirectResolver(max_redirects=max_redirects)
    assert resolver.resolve(server.many_redirects(max_redirects + 1)) == None

def test_cyclic_redirect(server):
    redirects_num = 3
    resolver = RedirectResolver()
    assert resolver.resolve(server.cyclic_redirect(redirects_num)) == None

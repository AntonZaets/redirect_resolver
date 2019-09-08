import pytest

from redirect_resolver import RedirectResolver
from redirect_server import RedirectServer

@pytest.fixture
def server():
    server = RedirectServer()
    server.start()
    yield server
    server.stop()

def test_many_redirects(server):
    redirects_num = 3
    resolver = RedirectResolver()
    assert resolver.resolve(server.many_redirects(redirects_num)) == None

def test_too_many_redirects(server):
    max_redirects = 1
    resolver = RedirectResolver(max_redirects=max_redirects)
    assert resolver.resolve(server.many_redirects(max_redirects + 1)) == None

def test_cyclic_redirect(server):
    resolver = RedirectResolver()
    assert resolver.resolve(server.cyclic_redirect()) == None

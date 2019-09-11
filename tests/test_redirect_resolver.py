import pytest

from redirect_resolver import RedirectResolver, TooManyRedirectsError, \
                              CyclicRedirectError
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
    url, target_url = server.many_redirects(redirects_num)
    assert resolver.resolve(url) == target_url

def test_too_many_redirects(server):
    max_redirects = 1
    resolver = RedirectResolver(max_redirects=max_redirects)
    url, _ = server.many_redirects(max_redirects + 1)
    with pytest.raises(TooManyRedirectsError):
        resolver.resolve(url)

def test_cyclic_redirect(server):
    redirects_num = 3
    resolver = RedirectResolver()
    with pytest.raises(CyclicRedirectError):
        resolver.resolve(server.cyclic_redirect(redirects_num))

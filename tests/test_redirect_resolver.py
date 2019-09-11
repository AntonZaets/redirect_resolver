import pytest

import redirect_resolver
import redirect_server

@pytest.fixture(scope='module')
def server():
    server = redirect_server.RedirectServer()
    server.start()
    yield server
    server.stop()

def test_no_redirects(server):
    resolver = redirect_resolver.RedirectResolver()
    url_without_redirects = server.no_redirects()
    assert resolver.resolve(url_without_redirects) == url_without_redirects

@pytest.mark.parametrize(
    'code', redirect_server.RedirectServer.get_redirect_codes())
def test_many_redirects(server, code):
    redirects_num = 3
    resolver = redirect_resolver.RedirectResolver()
    url, target_url = server.many_redirects(code, redirects_num)
    assert resolver.resolve(url) == target_url

@pytest.mark.parametrize(
    'code', redirect_server.RedirectServer.get_redirect_codes())
def test_too_many_redirects(server, code):
    max_redirects = 1
    resolver = redirect_resolver.RedirectResolver(max_redirects=max_redirects)
    url, _ = server.many_redirects(code, max_redirects + 1)
    with pytest.raises(redirect_resolver.TooManyRedirectsError):
        resolver.resolve(url)

@pytest.mark.parametrize(
    'code', redirect_server.RedirectServer.get_redirect_codes())
def test_cyclic_redirect(server, code):
    redirects_num = 3
    resolver = redirect_resolver.RedirectResolver(max_redirects=1000)
    with pytest.raises(redirect_resolver.CyclicRedirectError):
        resolver.resolve(server.cyclic_redirect(code, redirects_num))

def test_unlimited_content(server):
    resolver = redirect_resolver.RedirectResolver()
    with pytest.raises(redirect_resolver.UnlimitedContentError):
        resolver.resolve(server.unlimited_content())

def test_ignore_unlimited_content(server):
    resolver = redirect_resolver.RedirectResolver(ignore_unlimited=True)
    url = server.unlimited_content()
    assert resolver.resolve(url) == url

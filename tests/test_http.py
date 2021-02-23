import io

import pytest

from paaaaath import HttpPath, PureHttpPath
from paaaaath.http import _http_flavour


@pytest.mark.parametrize(
    ["partsstr", "expect"],
    [
        (
            ["http://example.com:80"],
            ("http://example.com:80", "/", ["http://example.com:80/"]),
        ),
        (
            ["https://example.com"],
            ("https://example.com", "/", ["https://example.com/"]),
        ),
    ],
)
def test_http_flavour_check_parse_parts(check_parse_parts, partsstr, expect):
    flavour = _http_flavour
    check_parse_parts(flavour, partsstr, expect)


@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("http://example.com", ("http://example.com", "/", "")),
        ("https://example.com", ("https://example.com", "/", "")),
    ],
)
def test_http_flavour_splitroot(pathstr, expect):
    f = _http_flavour.splitroot
    assert f(pathstr) == expect


@pytest.mark.parametrize(
    ["uri"],
    [
        ("s3://example.com",),
    ],
)
@pytest.mark.xfail(raises=ValueError)
def test_create_path_fail(uri):
    HttpPath(uri)


@pytest.mark.parametrize(
    ["uri", "resolve"],
    [
        (
            "http://example.com",
            HttpPath("http://example.com/"),
        ),
        (
            "http://user@example.com:80/foo/bar/piyo/../fuz",
            HttpPath("http://user@example.com:80/foo/bar/fuz"),
        ),
    ],
)
def test_http_path_resolve(uri, resolve):
    path = HttpPath(uri)

    assert path.resolve() == resolve


@pytest.mark.xfail(raises=NotImplementedError)
def test_gethome_fail():
    HttpPath.home()


@pytest.mark.xfail(raises=NotImplementedError)
def test_samefile_fail():
    HttpPath().samefile(HttpPath())


@pytest.mark.parametrize(["pathstr", "expect"], [("/foo", True), ("/bar", False)])
def test_exists(httpserver, pathstr, expect):
    httpserver.expect_request("/foo").respond_with_data()

    assert HttpPath(httpserver.url_for(pathstr)).exists() == expect


@pytest.mark.parametrize(
    ["mode", "file_cls", "expect"],
    [
        ({"mode": "r"}, io.TextIOBase, "this is file A"),
        ({"mode": "rb"}, io.BufferedIOBase, b"this is file A"),
        # ({"mode": "rb", "buffering": 0}, io.RawIOBase, b"this is file A"),
    ],
)
def test_open(httpserver, mode, file_cls, expect):
    httpserver.expect_request("/fileA").respond_with_data(expect)

    p = HttpPath(httpserver.url_for("/fileA"))
    with p.open(**mode) as f:
        assert isinstance(f, file_cls)
        assert f.read() == expect


@pytest.mark.parametrize(
    ["expect"],
    [
        (b"abcdefg",),
    ],
)
def test_read_bytes(httpserver, expect):
    httpserver.expect_request("/fileA").respond_with_data(expect)
    assert HttpPath(httpserver.url_for("/fileA")).read_bytes() == expect


@pytest.mark.parametrize(
    ["expect"],
    [
        ("abcdefg",),
    ],
)
def test_read_text(httpserver, expect):
    httpserver.expect_request("/fileA").respond_with_data(expect)
    assert HttpPath(httpserver.url_for("/fileA")).read_text() == expect
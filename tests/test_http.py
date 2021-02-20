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
            PureHttpPath("http://example.com/"),
        ),
        (
            "http://user@example.com:80/foo/bar/piyo/../fuz",
            PureHttpPath("http://user@example.com:80/foo/bar/fuz"),
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


@pytest.mark.xfail(raises=NotImplementedError)
def test_write_bytes_fail(httpserver):
    httpserver.expect_request("/fileA").respond_with_data()
    HttpPath(httpserver.url_for("/fileA")).write_bytes(b"a")


@pytest.mark.xfail(raises=NotImplementedError)
def test_writ_text_fail(httpserver):
    httpserver.expect_request("/fileA").respond_with_data()
    HttpPath(httpserver.url_for("/fileA")).write_text("a")


@pytest.mark.xfail(raises=NotImplementedError)
def test_iterdir_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    set(HttpPath(httpserver.url_for("/")).iterdir())


@pytest.mark.xfail(raises=NotImplementedError)
def test_glob_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    set(HttpPath(httpserver.url_for("/")).glob("fileA"))


@pytest.mark.xfail(raises=NotImplementedError)
def test_chmod_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).chmod(0)


@pytest.mark.xfail(raises=NotImplementedError)
def test_stat_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).stat()


@pytest.mark.xfail(raises=NotImplementedError)
def test_unlink_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).unlink()


@pytest.mark.xfail(raises=NotImplementedError)
def test_rename_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).rename("")


@pytest.mark.xfail(raises=NotImplementedError)
def test_replace_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).replace("")


@pytest.mark.xfail(raises=NotImplementedError)
def test_touch_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).touch()


@pytest.mark.xfail(raises=NotImplementedError)
def test_mkdir_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).mkdir()


@pytest.mark.xfail(raises=NotImplementedError)
def test_is_dir_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).is_dir()


@pytest.mark.xfail(raises=NotImplementedError)
def test_is_file_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).is_file()


@pytest.mark.xfail(raises=NotImplementedError)
def test_is_mount_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).is_mount()


@pytest.mark.xfail(raises=NotImplementedError)
def test_is_symlink_fail(httpserver):
    httpserver.expect_request("/").respond_with_data()
    HttpPath(httpserver.url_for("/")).is_symlink()

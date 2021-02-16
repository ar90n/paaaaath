from paaaaath import Path, PureHttpPath
from paaaaath.http import _http_flavour
import pytest


@pytest.mark.parametrize(
    ["actual", "expect"],
    [
        (["http://example.com"], ("http://example.com", "/", ["http://example.com/"])),
        (
            ["http://example.com:80"],
            ("http://example.com:80", "/", ["http://example.com:80/"]),
        ),
        (
            ["https://example.com"],
            ("https://example.com", "/", ["https://example.com/"]),
        ),
        (
            ["http://example.com", "abc", "def"],
            ("http://example.com", "/", ["http://example.com/", "abc", "def"]),
        ),
        (["http://", "abc", "def"], ("http://", "/", ["http:///", "abc", "def"])),
        (["http:", "abc", "def"], ("http://", "/", ["http:///", "abc", "def"])),
    ],
)
def test_http_flavour_check_parse_parts(check_parse_parts, actual, expect):
    flavour = _http_flavour
    # Protocol specified
    check_parse_parts(flavour, actual, expect)


@pytest.mark.parametrize(
    ["actual", "expect"],
    [
        ("", ("", "", "")),
        ("a", ("", "", "a")),
        ("a/b", ("", "", "a/b")),
        ("a/b/", ("", "", "a/b/")),
        ("/a", ("", "/", "a")),
        ("/a/b", ("", "/", "a/b")),
        ("/a/b/", ("", "/", "a/b/")),
        ("//a", ("", "/", "a")),
        ("///a", ("", "/", "a")),
        ("///a/b", ("", "/", "a/b")),
        ("\\/a/b", ("", "", "\\/a/b")),
        ("\\a\\b", ("", "", "\\a\\b")),
        ("http://example.com", ("http://example.com", "/", "")),
        ("http://example.com/abc/def", ("http://example.com", "/", "abc/def")),
        ("http:///abc/def", ("http://", "/", "abc/def")),
        ("http:/abc/def", ("http://", "/", "abc/def")),
    ],
)
def test_http_flavour_splitroot(actual, expect):
    f = _http_flavour.splitroot
    assert f(actual) == expect


@pytest.mark.parametrize(
    ["uri", "cls"],
    [
        ("http://example.com", PureHttpPath),
        ("https://example.com", PureHttpPath),
        ("http://example.com:80/index.html", PureHttpPath),
    ],
)
def test_create_path(uri, cls):
    path = Path(uri)

    assert isinstance(path, cls)


@pytest.mark.parametrize(
    ["uri", "drive", "root", "anchor", "rest_parts", "as_uri"],
    [
        (
            "http://example.com",
            "http://example.com",
            "/",
            "http://example.com/",
            (),
            "http://example.com/",
        ),
        (
            "https://example.com",
            "https://example.com",
            "/",
            "https://example.com/",
            (),
            "https://example.com/",
        ),
        (
            "http://example.com:80/foo/bar/piyo/../fuz",
            "http://example.com:80",
            "/",
            "http://example.com:80/",
            ("foo", "bar", "piyo", "..", "fuz"),
            "http://example.com:80/foo/bar/piyo/../fuz",
        ),
    ],
)
def test_uri_parsing(uri, drive, root, anchor, rest_parts, as_uri):
    path = PureHttpPath(uri)

    assert path.drive == drive
    assert path.root == root
    assert path.anchor == anchor
    assert path.parts[1:] == rest_parts
    assert path.as_uri() == as_uri
    assert str(path) == path.as_uri()
    assert path.as_posix() == path.as_uri()


@pytest.mark.parametrize(
    ["uri", "name", "suffix", "suffixes", "stem", "parent", "parts"],
    [
        (
            "http://example.com/foo/bar/buz/index.html",
            "index.html",
            ".html",
            [".html"],
            "index",
            PureHttpPath("http://example.com/foo/bar/buz"),
            ("http://example.com/", "foo", "bar", "buz", "index.html"),
        ),
        (
            "http://example.com/foo",
            "foo",
            "",
            [],
            "foo",
            PureHttpPath("http://example.com/"),
            ("http://example.com/", "foo"),
        ),
        (
            "http://example.com/",
            "",
            "",
            [],
            "",
            PureHttpPath("http://example.com/"),
            ("http://example.com/",),
        ),
    ],
)
def test_getting_parts(uri, name, suffix, suffixes, stem, parent, parts):
    path = PureHttpPath(uri)

    assert path.name == name
    assert path.suffix == suffix
    assert path.suffixes == suffixes
    assert path.stem == stem
    assert path.parent == parent
    assert path.parts == parts


@pytest.mark.parametrize(
    ["uri", "with_name", "with_stem", "with_suffix"],
    [
        (
            "http://example.com/index.html",
            ("mod.jpg", PureHttpPath("http://example.com/mod.jpg")),
            ("mod", PureHttpPath("http://example.com/mod.html")),
            (".jpg", PureHttpPath("http://example.com/index.jpg")),
        )
    ],
)
def test_path_modifications(uri, with_name, with_stem, with_suffix):
    path = PureHttpPath(uri)

    assert path.with_name(with_name[0]) == with_name[1]
    assert path.with_stem(with_stem[0]) == with_stem[1]
    assert path.with_suffix(with_suffix[0]) == with_suffix[1]


@pytest.mark.parametrize(
    ["uri", "is_absolute", "is_reserved"],
    [
        (
            "http://example.com/index.html",
            True,
            False,
        )
    ],
)
def test_predicates(uri, is_absolute, is_reserved):
    path = PureHttpPath(uri)

    assert path.is_absolute() == is_absolute
    assert path.is_reserved() == is_reserved


@pytest.mark.parametrize(
    ["uri", "parents"],
    [
        (
            "http://example.com/foo/bar/buz/tmp.html",
            (
                PureHttpPath("http://example.com/foo/bar/buz"),
                PureHttpPath("http://example.com/foo/bar"),
                PureHttpPath("http://example.com/foo"),
                PureHttpPath("http://example.com/"),
            ),
        )
    ],
)
def test_parents(uri, parents):
    path = PureHttpPath(uri)

    assert tuple(path.parents) == parents


#    def joinpath(self, *args):
#    def match(self, path_pattern):


# @pytest.mark.parametrize(
#    ["uri", "dst_uri", "relative_to", "is_relative_to"],
#    [
#        (
#            "http://example.com/foo/bar/buz/tmp/abc.jpg",
#            "http://example.com/foo/bar/",
#            "buz/tmpm/abc.jpg",
#            True
#        )
#    ],
# )
# def test_relative_path_failed(uri, dst_uri, relative_to, is_relative_to):
#    path = PureHttpPath(uri)
#
#    assert path.relative_to(dst_uri) == relative_to
#    assert path.is_relative_to(dst_uri) == is_relative_to


# def test_read_text_http_path():
#    # p = PureHttpPath("http://google.com")
#    p = PureHttpPath(
#        "https://www.google.com/search?sa=X&q=%E3%83%90%E3%83%AC%E3%83%B3%E3%82%BF%E3%82%A4%E3%83%B3%E3%83%87%E3%83%BC&oi=ddle&ct=174786504&hl=ja&ved=0ahUKEwiHtvL5yunuAhUCMN4KHd7ICq4QPQgE&biw=1276&bih=1336"
#    )
#    txt = p.read_text()
#    assert txt is None
#


@pytest.mark.parametrize(
    ["uri", "resolve"],
    [
        (
            "http://example.com",
            PureHttpPath("http://example.com/"),
        ),
        (
            "http://example.com:80/foo/bar/piyo/../fuz",
            PureHttpPath("http://example.com:80/foo/bar/fuz"),
        ),
    ],
)
def test_http_path_resolve(uri, resolve):
    from paaaaath import HttpPath

    path = HttpPath(uri)

    assert path.resolve() == resolve

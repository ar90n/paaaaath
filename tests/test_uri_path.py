import pytest

from paaaaath.uri import _uri_flavour, PureUriPath


@pytest.mark.parametrize(
    ["partsstr", "expect"],
    [
        (["http://example.com"], ("http://example.com", "/", ["http://example.com/"])),
        (
            ["http://user@example.com:80"],
            ("http://user@example.com:80", "/", ["http://user@example.com:80/"]),
        ),
        (
            ["http://example.com", "abc", "def"],
            ("http://example.com", "/", ["http://example.com/", "abc", "def"]),
        ),
        (["http://", "abc", "def"], ("http://", "/", ["http:///", "abc", "def"])),
        (["http:", "abc", "def"], ("http://", "/", ["http:///", "abc", "def"])),
    ],
)
def test_http_flavour_check_parse_parts(check_parse_parts, partsstr, expect):
    flavour = _uri_flavour
    check_parse_parts(flavour, partsstr, expect)


@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("http://user@example.com", ("http://user@example.com", "/", "")),
        ("http://example.com/abc/def", ("http://example.com", "/", "abc/def")),
        ("http:///abc/def", ("http://", "/", "abc/def")),
        ("http:/abc/def", ("http://", "/", "abc/def")),
    ],
)
def test_http_flavour_splitroot(pathstr, expect):
    f = _uri_flavour.splitroot
    assert f(pathstr) == expect


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
            "http://user@example.com:80/foo/bar/piyo/../fuz",
            "http://user@example.com:80",
            "/",
            "http://user@example.com:80/",
            ("foo", "bar", "piyo", "..", "fuz"),
            "http://user@example.com:80/foo/bar/piyo/../fuz",
        ),
    ],
)
def test_uri_parsing(uri, drive, root, anchor, rest_parts, as_uri):
    path = PureUriPath(uri)

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
            "s3://example.com/foo/bar/buz/index.html",
            "index.html",
            ".html",
            [".html"],
            "index",
            PureUriPath("s3://example.com/foo/bar/buz"),
            ("s3://example.com/", "foo", "bar", "buz", "index.html"),
        ),
        (
            "s3://example.com/foo",
            "foo",
            "",
            [],
            "foo",
            PureUriPath("s3://example.com/"),
            ("s3://example.com/", "foo"),
        ),
        (
            "s3://example.com/",
            "",
            "",
            [],
            "",
            PureUriPath("s3://example.com/"),
            ("s3://example.com/",),
        ),
    ],
)
def test_getting_parts(uri, name, suffix, suffixes, stem, parent, parts):
    path = PureUriPath(uri)

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
            "gcp://example.com/index.html",
            ("mod.jpg", PureUriPath("gcp://example.com/mod.jpg")),
            ("mod", PureUriPath("gcp://example.com/mod.html")),
            (".jpg", PureUriPath("gcp://example.com/index.jpg")),
        )
    ],
)
def test_path_modifications(uri, with_name, with_stem, with_suffix):
    path = PureUriPath(uri)

    assert path.with_name(with_name[0]) == with_name[1]
    assert path.with_stem(with_stem[0]) == with_stem[1]
    assert path.with_suffix(with_suffix[0]) == with_suffix[1]


@pytest.mark.parametrize(
    ["uri", "is_absolute"],
    [
        (
            "http://example.com/index.html",
            True,
        )
    ],
)
def test_is_absolute(uri, is_absolute):
    path = PureUriPath(uri)

    assert path.is_absolute() == is_absolute


@pytest.mark.parametrize(
    ["uri", "parents"],
    [
        (
            "https://example.com/foo/bar/buz/tmp.html",
            (
                PureUriPath("https://example.com/foo/bar/buz"),
                PureUriPath("https://example.com/foo/bar"),
                PureUriPath("https://example.com/foo"),
                PureUriPath("https://example.com/"),
            ),
        )
    ],
)
def test_parents(uri, parents):
    path = PureUriPath(uri)

    assert tuple(path.parents) == parents


@pytest.mark.parametrize(
    ["uri", "succ", "expect"],
    [
        (
            "http://example.com/",
            "/foo/bar",
            PureUriPath("http://example.com/foo/bar"),
        ),
        (
            "http://example.com/foo",
            "../bar",
            PureUriPath("http://example.com/foo/../bar"),
        ),
        (
            "http://example.com/",
            "s3://example.com/",
            PureUriPath("s3://example.com"),
        ),
    ],
)
def test_joinpath(uri, succ, expect):
    assert PureUriPath(uri).joinpath(succ) == expect


@pytest.mark.parametrize(
    ["uri", "part", "expect"],
    [
        ("http://example.com/b.py", "b.py", True),
        ("http://example.com/b.py", "example.com", False),
    ],
)
def test_match(uri, part, expect):
    assert PureUriPath(uri).match(part) == expect

import os
import pickle

import pytest

import paaaaath
from paaaaath import (HttpPath, Path, PosixPath, PureHttpPath, PurePath,
                      PurePosixPath, PureS3Path, PureUriPath, PureWindowsPath,
                      S3Path, WindowsPath)

pure_path_classes = [(PureUriPath,), (PureHttpPath,), (PureS3Path,)]


class FakePath:
    """Simple implementing of the path protocol."""

    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f"<FakePath {self.path!r}>"

    def __fspath__(self):
        if (
            isinstance(self.path, BaseException)
            or isinstance(self.path, type)
            and issubclass(self.path, BaseException)
        ):
            raise self.path
        else:
            return self.path


@pytest.mark.parametrize(
    ["uri", "cls"],
    [
        ("http://example.com", PureHttpPath),
        ("https://example.com", PureHttpPath),
        ("http://example.com:80/index.html", PureHttpPath),
        ("s3://example.com", PureS3Path),
        ("/example.com", PureWindowsPath if os.name == "nt" else PurePosixPath),
    ],
)
def test_create_purepath(uri, cls):
    path = PurePath(uri)
    assert isinstance(path, cls)


@pytest.mark.parametrize(
    ["uri", "cls"],
    [
        ("http://example.com", HttpPath),
        ("https://example.com", HttpPath),
        ("http://example.com:80/index.html", HttpPath),
        ("s3://example.com", S3Path),
        ("/example.com", WindowsPath if os.name == "nt" else PosixPath),
    ],
)
def test_create_path(uri, cls):
    path = Path(uri)
    assert isinstance(path, cls)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["partsstr", "expect"],
    [
        ([], ("", "", [])),
        (["a"], ("", "", ["a"])),
        (["a/"], ("", "", ["a"])),
        (["a", "b"], ("", "", ["a", "b"])),
        (["a/b"], ("", "", ["a", "b"])),
        (["a/b/"], ("", "", ["a", "b"])),
        (["a", "b/c", "d"], ("", "", ["a", "b", "c", "d"])),
        (["a", "b//c", "d"], ("", "", ["a", "b", "c", "d"])),
        (["a", "b/c/", "d"], ("", "", ["a", "b", "c", "d"])),
        (["."], ("", "", [])),
        ([".", ".", "b"], ("", "", ["b"])),
        (["a", ".", "b"], ("", "", ["a", "b"])),
        (["a", ".", "."], ("", "", ["a"])),
        (["/a/b"], ("", "/", ["/", "a", "b"])),
        (["/a", "b"], ("", "/", ["/", "a", "b"])),
        (["/a/", "b"], ("", "/", ["/", "a", "b"])),
        (["a", "/b", "c"], ("", "/", ["/", "b", "c"])),
        (["a", "/b", "/c"], ("", "/", ["/", "c"])),
        (["//a", "b"], ("", "/", ["/", "a", "b"])),
        (["///a", "b"], ("", "/", ["/", "a", "b"])),
        (["////a", "b"], ("", "/", ["/", "a", "b"])),
        (["\\a"], ("", "", ["\\a"])),
    ],
)
def test_flavour_check_parse_parts(check_parse_parts, pure_path_cls, partsstr, expect):
    check_parse_parts(pure_path_cls._flavour, partsstr, expect)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"],
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
    ],
)
def test_flavour_splitroot(pure_path_cls, pathstr, expect):
    assert pure_path_cls._flavour.splitroot(pathstr) == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_purepath_constructor(pure_path_cls):
    P = pure_path_cls
    p = P("a")
    assert isinstance(p, P)
    P("a", "b", "c")
    P("/a", "b", "c")
    P("a/b/c")
    P("/a/b/c")
    P(FakePath("a/b/c"))
    assert P(P("a")) == P("a")
    assert P(P("a"), "b") == P("a/b")
    assert P(P("a"), P("b")) == P("a/b")
    assert P(P("a"), P("b"), P("c")) == P(FakePath("a/b/c"))


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr"], [("",), (".",), ("a",), ("a/b.txt",), ("/a/b.txt",)]
)
def test_check_str_subclass(check_str_subclass, pure_path_cls, pathstr):
    check_str_subclass(pure_path_cls, pathstr)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "f", "expect"],
    [
        ("a/b", lambda _: _.joinpath("c"), "a/b/c"),
        ("a/b", lambda _: _.joinpath("c", "d"), "a/b/c/d"),
        ("a/b", lambda _: _.joinpath("c"), "a/b/c"),
        ("a/b", lambda _: _.joinpath("/c"), "/c"),
        ("//a", lambda _: _.joinpath("b"), "//a/b"),
        ("/a", lambda _: _.joinpath("//c"), "//c"),
        ("//a", lambda _: _.joinpath("/c"), "/c"),
    ],
)
def test_join(pure_path_cls, pathstr, f, expect):
    P = pure_path_cls
    p = P(pathstr)
    pp = f(p)
    assert pp == P(expect)
    assert type(pp) is type(p)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "f", "expect"],
    [
        ("a/b", lambda _: _ / "c", "a/b/c"),
        ("a/b", lambda _: _ / "c/d", "a/b/c/d"),
        ("a/b", lambda _: _ / "c" / "d", "a/b/c/d"),
        ("a/b", lambda _: "c" / _ / "d", "c/a/b/d"),
        ("a/b", lambda _: _ / "/c", "/c"),
        ("a/b", lambda _: _ / type(_)("c"), "a/b/c"),
        ("//a", lambda _: _ / "b", "//a/b"),
        ("/a", lambda _: _ / "//c", "//c"),
        ("//a", lambda _: _ / "/c", "/c"),
    ],
)
def test_div(pure_path_cls, pathstr, f, expect):
    P = pure_path_cls
    p = P(pathstr)
    pp = f(p)
    assert pp == P(expect)
    assert type(pp) == type(p)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr"], [("a",), ("a/b",), ("a/b/c",), ("/",), ("/a/b",), ("/a/b/c",)]
)
def test_str(check_str, pure_path_cls, pathstr):
    check_str(pure_path_cls, pathstr, (pathstr,))
    check_str(pure_path_cls, ".", ("",))


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr"], [("a",), ("a/b",), ("a/b/c",), ("/",), ("/a/b",), ("/a/b/c",)]
)
def test_as_posix(pure_path_cls, pathstr):
    P = pure_path_cls
    assert P(pathstr).as_posix() == pathstr


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_as_bytes(pure_path_cls):
    sep = os.fsencode(pure_path_cls._flavour.sep)
    P = pure_path_cls
    assert bytes(P("a/b")) == b"a" + sep + b"b"


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(["pathstr"], [("a",), ("",)])
@pytest.mark.xfail(raises=ValueError)
def test_as_uri_failed(pure_path_cls, pathstr):
    P = pure_path_cls
    P(pathstr).as_uri()


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr"], [("a",), ("a/b",), ("a/b/c",), ("/",), ("/a/b",), ("/a/b/c",)]
)
def test_repr(pure_path_cls, pathstr):
    p = pure_path_cls(pathstr)
    clsname = p.__class__.__name__
    r = repr(p)
    # The repr() is in the form ClassName("forward-slashes path").
    assert r.startswith(clsname + "(")
    assert r.endswith(")")
    inner = r[len(clsname) + 1 : -1]
    assert eval(inner) == p.as_posix()
    # The repr() roundtrips.
    q = eval(r, paaaaath.__dict__)
    assert q.__class__ is p.__class__
    assert q == p
    assert repr(q) == r


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_eq(pure_path_cls):
    P = pure_path_cls
    assert P("a/b") == P("a/b")
    assert P("a/b") == P("a", "b")
    assert P("a/b") != P("a")
    assert P("a/b") != P("/a/b")
    assert P("a/b") != P()
    assert P("/a/b") != P("/")
    assert P() != P("/")
    assert P() != ""
    assert P() != {}
    assert P() != int


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr"],
    [
        ("",),
        (".",),
    ],
)
@pytest.mark.xfail(raises=ValueError)
def test_match_fail(pure_path_cls, pathstr):
    P = pure_path_cls
    P("a").match(pathstr)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "part", "expect"],
    [
        ("b.py", "b.py", True),
        ("a/b.py", "b.py", True),
        ("/a/b.py", "b.py", True),
        ("b.py", "*.py", True),
        ("a/b.py", "*.py", True),
        ("/a/b.py", "*.py", True),
        ("ab/c.py", "a*/*.py", True),
        ("/d/ab/c.py", "a*/*.py", True),
        ("/b.py", "/*.py", True),
        ("/a/b.py", "/a/*.py", True),
        ("/a/b/c.py", "/a/**/*.py", True),
        ("a.py", "b.py", False),
        ("b/py", "b.py", False),
        ("/a.py", "b.py", False),
        ("b.py/c", "b.py", False),
        ("b.pyc", "*.py", False),
        ("b./py", "*.py", False),
        ("b.py/c", "*.py", False),
        ("a.py", "a*/*.py", False),
        ("/dab/c.py", "a*/*.py", False),
        ("ab/c.py/d", "a*/*.py", False),
        ("b.py", "/*.py", False),
        ("a/b.py", "/*.py", False),
        ("/a/b.py", "/*.py", False),
        ("/ab.py", "/a/*.py", False),
        ("/a/b/c.py", "/a/*.py", False),
        ("/a/b/c.py", "/**/*.py", False),
        ("A.py", "a.PY", False),
    ],
)
def test_match(pure_path_cls, pathstr, part, expect):
    P = pure_path_cls
    assert P(pathstr).match(part) == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["a", "b", "c", "d"], [("a", "a/b", "abc", "b"), ("/a", "/a/b", "/abc", "/b")]
)
def test_ordering(pure_path_cls, a, b, c, d):
    P = pure_path_cls
    assert P(a) < P(b) < P(c) < P(d)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.xfail(raises=TypeError)
def test_ordering_fail(pure_path_cls):
    pure_path_cls() < {}


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"], [("a/b", ("a", "b")), ("/a/b", ("/", "a", "b"))]
)
def test_parts(pure_path_cls, pathstr, expect):
    P = pure_path_cls
    p = P(pathstr)
    assert p.parts == expect
    assert p.parts is p.parts


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_fspath(check_str, pure_path_cls):
    P = pure_path_cls
    p = P("a/b")
    check_str(P, p.__fspath__(), ("a/b",))
    check_str(P, os.fspath(p), ("a/b",))


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "equivalences"],
    [
        (
            "a/b",
            [
                ("a", "b"),
                ("a/", "b"),
                ("a", "b/"),
                ("a/", "b/"),
                ("a/b/",),
                ("a//b",),
                ("a//b//",),
                ("", "a", "b"),
                ("a", "", "b"),
                ("a", "b", ""),
            ],
        ),
        (
            "/b/c/d",
            [
                ("a", "/b/c", "d"),
                ("a", "///b//c", "d/"),
                ("/a", "/b/c", "d"),
                ("/", "b", "", "c/d"),
                ("/", "", "b/c/d"),
                ("", "/b/c/d"),
            ],
        ),
    ],
)
def test_equivalences(pure_path_cls, pathstr, equivalences):
    oracle = pure_path_cls(pathstr)
    for parts in equivalences:
        p = pure_path_cls(*parts)
        assert p == oracle
        assert hash(p) == hash(oracle)
        assert str(p) == pathstr
        assert p.as_posix() == pathstr


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "p0", "p1", "p2", "p3"],
    [("a/b/c", "a/b", "a", "", ""), ("/a/b/c", "/a/b", "/a", "/", "/")],
)
def test_parent(pure_path_cls, pathstr, p0, p1, p2, p3):
    P = pure_path_cls
    p = P(pathstr)
    assert p.parent == P(p0)
    assert p.parent.parent == P(p1)
    assert p.parent.parent.parent == P(p2)
    assert p.parent.parent.parent.parent == P(p3)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_parents(pure_path_cls):
    # Relative
    P = pure_path_cls
    p = P("a/b/c")
    par = tuple(p.parents)
    assert len(par) == 3
    assert par[0] == P("a/b")
    assert par[1] == P("a")
    assert par[2] == P(".")
    assert par[-1] == P(".")
    assert par[-2] == P("a")
    assert par[-3] == P("a/b")
    assert par[0:1] == (P("a/b"),)
    assert par[:2] == (P("a/b"), P("a"))
    assert par[:-1] == (P("a/b"), P("a"))
    assert par[1:] == (P("a"), P("."))
    assert par[::2] == (P("a/b"), P("."))
    assert par[::-1] == (P("."), P("a"), P("a/b"))
    assert list(par) == [P("a/b"), P("a"), P(".")]
    with pytest.raises(IndexError):
        par[-4]
    with pytest.raises(IndexError):
        par[3]
    with pytest.raises(TypeError):
        par[0] = p
    # Anchored
    p = P("/a/b/c")
    par = tuple(p.parents)
    assert len(par) == 3
    assert par[0] == P("/a/b")
    assert par[1] == P("/a")
    assert par[2] == P("/")
    assert par[0:1] == (P("/a/b"),)
    assert par[:2] == (P("/a/b"), P("/a"))
    assert par[:-1] == (P("/a/b"), P("/a"))
    assert par[1:] == (P("/a"), P("/"))
    assert par[::2] == (P("/a/b"), P("/"))
    assert par[::-1] == (P("/"), P("/a"), P("/a/b"))
    assert list(par) == [P("/a/b"), P("/a"), P("/")]
    with pytest.raises(IndexError):
        par[3]


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(["pathstr"], [("a/b",), ("/a/b",), ("",)])
def test_drive(pure_path_cls, pathstr):
    P = pure_path_cls
    assert P(pathstr).drive == ""


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [("", ""), ("a/b", ""), ("/", "/"), ("/a/b", "/"), ("///a/b", "/"), ("//a/b", "/")],
)
def test_root(pure_path_cls, pathstr, expect):
    assert pure_path_cls(pathstr).root == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [("", ""), ("a/b", ""), ("/", "/"), ("/a/b", "/")],
)
def test_anchor(pure_path_cls, pathstr, expect):
    P = pure_path_cls
    assert P(pathstr).anchor == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("", ""),
        (".", ""),
        ("/", ""),
        ("a/b", "b"),
        ("/a/b", "b"),
        ("/a/b/.", "b"),
        ("a/b.py", "b.py"),
        ("/a/b.py", "b.py"),
    ],
)
def test_name(pure_path_cls, pathstr, expect):
    P = pure_path_cls
    assert P(pathstr).name == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("", ""),
        ("/", ""),
        ("a/b", ""),
        ("/a/b", ""),
        ("/a/b/.", ""),
        ("a/b.py", ".py"),
        ("/a/b.py", ".py"),
        ("a/.hgrc", ""),
        ("/a/.hgrc", ""),
        ("a/.hg.rc", ".rc"),
        ("/a/.hg.rc", ".rc"),
        ("a/b.tar.gz", ".gz"),
        ("/a/b.tar.gz", ".gz"),
        ("a/Some name. Ending with a dot.", ""),
        ("/a/Some name. Ending with a dot.", ""),
    ],
)
def test_suffix(pure_path_cls, pathstr, expect):
    P = pure_path_cls
    assert P(pathstr).suffix == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("", []),
        (".", []),
        ("/", []),
        ("a/b", []),
        ("/a/b", []),
        ("/a/b/.", []),
        ("a/b.py", [".py"]),
        ("/a/b.py", [".py"]),
        ("a/.hgrc", []),
        ("/a/.hgrc", []),
        ("a/.hg.rc", [".rc"]),
        ("/a/.hg.rc", [".rc"]),
        ("a/b.tar.gz", [".tar", ".gz"]),
        ("/a/b.tar.gz", [".tar", ".gz"]),
        ("a/Some name. Ending with a dot.", []),
        ("/a/Some name. Ending with a dot.", []),
    ],
)
def test_suffixes(pure_path_cls, pathstr, expect):
    P = pure_path_cls
    assert P(pathstr).suffixes == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("", ""),
        (".", ""),
        ("..", ".."),
        ("/", ""),
        ("a/b", "b"),
        ("a/b.py", "b"),
        ("a/.hgrc", ".hgrc"),
        ("a/.hg.rc", ".hg"),
        ("a/b.tar.gz", "b.tar"),
        ("a/Some name. Ending with a dot.", "Some name. Ending with a dot."),
    ],
)
def test_stem(pure_path_cls, pathstr, expect):
    P = pure_path_cls
    assert P(pathstr).stem == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "namestr", "expect"],
    [
        ("a/b", "d.xml", "a/d.xml"),
        ("/a/b", "d.xml", "/a/d.xml"),
        ("a/b.py", "d.xml", "a/d.xml"),
        ("/a/b.py", "d.xml", "/a/d.xml"),
        ("a/Dot ending.", "d.xml", "a/d.xml"),
        ("/a/Dot ending.", "d.xml", "/a/d.xml"),
    ],
)
def test_with_name(pure_path_cls, pathstr, namestr, expect):
    P = pure_path_cls
    assert P(pathstr).with_name(namestr) == P(expect)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "name"],
    [
        ("", "d.xml"),
        (".", "d.xml"),
        ("/", "d.xml"),
        ("a/b", ""),
        ("a/b", "/c"),
        ("a/b", "c/"),
        ("a/b", "c/d"),
    ],
)
@pytest.mark.xfail(raises=ValueError)
def test_with_name_fail(pure_path_cls, pathstr, name):
    pure_path_cls(pathstr).with_name(name)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "stemstr", "expect"],
    [
        ("a/b", "d", "a/d"),
        ("/a/b", "d", "/a/d"),
        ("a/b.py", "d", "a/d.py"),
        ("/a/b.tar.gz", "d", "/a/d.gz"),
        ("a/Dot ending.", "d", "a/d"),
        ("/a/Dot ending.", "d", "/a/d"),
    ],
)
def test_with_stem(pure_path_cls, pathstr, stemstr, expect):
    P = pure_path_cls
    assert P(pathstr).with_stem(stemstr) == P(expect)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "stem"],
    [
        ("", "d"),
        (".", "d"),
        ("/", "d"),
        ("a/b", ""),
        ("a/b", "/c"),
        ("a/b", "c/"),
        ("a/b", "c/d"),
    ],
)
@pytest.mark.xfail(raises=ValueError)
def test_with_stem_fail(pure_path_cls, pathstr, stem):
    pure_path_cls(pathstr).with_stem(stem)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "suffixstr", "expect"],
    [
        ("a/b", ".gz", "a/b.gz"),
        ("/a/b", ".gz", "/a/b.gz"),
        ("a/b.py", ".gz", "a/b.gz"),
        ("/a/b.py", ".gz", "/a/b.gz"),
        ("a/b.py", "", "a/b"),
        ("/a/b", "", "/a/b"),
    ],
)
def test_with_suffix(pure_path_cls, pathstr, suffixstr, expect):
    P = pure_path_cls
    assert P(pathstr).with_suffix(suffixstr) == P(expect)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "suffix"],
    [
        ("", ".gz"),
        (".", ".gz"),
        ("/", ".gz"),
        ("a/b", "gz"),
        ("a/b", "/"),
        ("a/b", "."),
        ("a/b", "/.gz"),
        ("a/b", "c/d"),
        ("a/b", ".c/.d"),
        ("a/b", "./.d"),
        ("a/b", ".d/."),
        ("a/b", ("/", "d")),
    ],
)
@pytest.mark.xfail(raises=ValueError)
def test_with_suffix_fail(pure_path_cls, pathstr, suffix):
    pure_path_cls(pathstr).with_suffix(suffix)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_relative_to(pure_path_cls):
    P = pure_path_cls
    p = P("a/b")
    assert p.relative_to(P()) == P("a/b")
    assert p.relative_to("") == P("a/b")
    assert p.relative_to(P("a")) == P("b")
    assert p.relative_to("a") == P("b")
    assert p.relative_to("a/") == P("b")
    assert p.relative_to(P("a/b")) == P()
    assert p.relative_to("a/b") == P()
    with pytest.raises(TypeError):
        p.relative_to()
    with pytest.raises(TypeError):
        p.relative_to(b"a")
    # With several args.
    assert p.relative_to("a", "b") == P()
    # Unrelated paths.
    with pytest.raises(ValueError):
        p.relative_to(P("c"))
    with pytest.raises(ValueError):
        p.relative_to(P("a/b/c"))
    with pytest.raises(ValueError):
        p.relative_to(P("a/c"))
    with pytest.raises(ValueError):
        p.relative_to(P("/a"))
    p = P("/a/b")
    assert p.relative_to(P("/")) == P("a/b")
    assert p.relative_to("/") == P("a/b")
    assert p.relative_to(P("/a")) == P("b")
    assert p.relative_to("/a") == P("b")
    assert p.relative_to("/a/") == P("b")
    assert p.relative_to(P("/a/b")) == P()
    assert p.relative_to("/a/b") == P()
    # Unrelated paths.
    with pytest.raises(ValueError):
        p.relative_to(P("/c"))
    with pytest.raises(ValueError):
        p.relative_to(P("/a/b/c"))
    with pytest.raises(ValueError):
        p.relative_to(P("/a/c"))
    with pytest.raises(ValueError):
        p.relative_to(P())
    with pytest.raises(ValueError):
        p.relative_to("")
    with pytest.raises(ValueError):
        p.relative_to(P("a"))


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_is_relative_to(pure_path_cls):
    P = pure_path_cls
    p = P("a/b")
    with pytest.raises(TypeError):
        p.is_relative_to()
    with pytest.raises(TypeError):
        p.is_relative_to(b"a")
    assert p.is_relative_to(P())
    assert p.is_relative_to("")
    assert p.is_relative_to(P("a"))
    assert p.is_relative_to("a/")
    assert p.is_relative_to(P("a/b"))
    assert p.is_relative_to("a/b")
    # With several args.
    assert p.is_relative_to("a", "b")
    # Unrelated paths.
    assert not (p.is_relative_to(P("c")))
    assert not (p.is_relative_to(P("a/b/c")))
    assert not (p.is_relative_to(P("a/c")))
    assert not (p.is_relative_to(P("/a")))
    p = P("/a/b")
    assert p.is_relative_to(P("/"))
    assert p.is_relative_to("/")
    assert p.is_relative_to(P("/a"))
    assert p.is_relative_to("/a")
    assert p.is_relative_to("/a/")
    assert p.is_relative_to(P("/a/b"))
    assert p.is_relative_to("/a/b")
    # Unrelated paths.
    assert not (p.is_relative_to(P("/c")))
    assert not (p.is_relative_to(P("/a/b/c")))
    assert not (p.is_relative_to(P("/a/c")))
    assert not (p.is_relative_to(P()))
    assert not (p.is_relative_to(""))
    assert not (p.is_relative_to(P("a")))


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_pickling(pure_path_cls):
    P = pure_path_cls
    p = P("/a/b")
    for proto in range(0, pickle.HIGHEST_PROTOCOL + 1):
        dumped = pickle.dumps(p, proto)
        pp = pickle.loads(dumped)
        assert pp.__class__ is p.__class__
        assert pp == p
        assert hash(pp) == hash(p)
        assert str(pp) == str(p)


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["left_hand", "right_hand", "expect"],
    [("/a/b/b", "A/b", False), ("/a", "///a", True), ("/a", "//a", True)],
)
def test_eq(pure_path_cls, left_hand, right_hand, expect):
    assert (pure_path_cls(left_hand) == pure_path_cls(right_hand)) == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("/", False),
        ("/a", False),
        ("/a/b/", False),
        ("//a", False),
        ("//a/b", False),
        ("", False),
        ("a", False),
        ("a/b/", False),
    ],
)
def test_is_absolute(pure_path_cls, pathstr, expect):
    P = pure_path_cls
    assert P(pathstr).is_absolute() == expect


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("", False),
        ("/", False),
        ("/foo/bar", False),
        ("/dev/con/PRN/NUL", False),
    ],
)
def test_is_reserved(pure_path_cls, pathstr, expect):
    assert pure_path_cls(pathstr).is_reserved() == expect

import os
import pickle

import pytest

import paaaaath
from paaaaath.http import _http_flavour, PureHttpPath


pure_path_classes = [(PureHttpPath,)]


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


@pytest.mark.parametrize(["flavour"], [(_http_flavour,)])
def test_flavour_check_parse_parts(check_parse_parts, flavour):
    sep = flavour.sep
    # Unanchored parts.
    check_parse_parts(flavour, [], ("", "", []))
    check_parse_parts(flavour, ["a"], ("", "", ["a"]))
    check_parse_parts(flavour, ["a/"], ("", "", ["a"]))
    check_parse_parts(flavour, ["a", "b"], ("", "", ["a", "b"]))
    # Expansion.
    check_parse_parts(flavour, ["a/b"], ("", "", ["a", "b"]))
    check_parse_parts(flavour, ["a/b/"], ("", "", ["a", "b"]))
    check_parse_parts(flavour, ["a", "b/c", "d"], ("", "", ["a", "b", "c", "d"]))
    # Collapsing and stripping excess slashes.
    check_parse_parts(flavour, ["a", "b//c", "d"], ("", "", ["a", "b", "c", "d"]))
    check_parse_parts(flavour, ["a", "b/c/", "d"], ("", "", ["a", "b", "c", "d"]))
    # Eliminating standalone dots.
    check_parse_parts(flavour, ["."], ("", "", []))
    check_parse_parts(flavour, [".", ".", "b"], ("", "", ["b"]))
    check_parse_parts(flavour, ["a", ".", "b"], ("", "", ["a", "b"]))
    check_parse_parts(flavour, ["a", ".", "."], ("", "", ["a"]))
    # The first part is anchored.
    check_parse_parts(flavour, ["/a/b"], ("", sep, [sep, "a", "b"]))
    check_parse_parts(flavour, ["/a", "b"], ("", sep, [sep, "a", "b"]))
    check_parse_parts(flavour, ["/a/", "b"], ("", sep, [sep, "a", "b"]))
    # Ignoring parts before an anchored part.
    check_parse_parts(flavour, ["a", "/b", "c"], ("", sep, [sep, "b", "c"]))
    check_parse_parts(flavour, ["a", "/b", "/c"], ("", sep, [sep, "c"]))
    # special case
    check_parse_parts(flavour, ["//a", "b"], ("", sep, [sep, "a", "b"]))
    check_parse_parts(flavour, ["///a", "b"], ("", sep, [sep, "a", "b"]))
    check_parse_parts(flavour, ["////a", "b"], ("", sep, [sep, "a", "b"]))
    check_parse_parts(flavour, ["\\a"], ("", "", ["\\a"]))


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
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


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
def test_check_str_subclass(check_str_subclass, pure_path_cls):
    check_str_subclass(pure_path_cls, "")
    check_str_subclass(pure_path_cls, ".")
    check_str_subclass(pure_path_cls, "a")
    check_str_subclass(pure_path_cls, "a/b.txt")
    check_str_subclass(pure_path_cls, "/a/b.txt")


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
def test_join(pure_path_cls):
    P = pure_path_cls
    p = P("a/b")
    pp = p.joinpath("c")
    assert pp == P("a/b/c")
    assert type(pp) is type(p)
    pp = p.joinpath("c", "d")
    assert pp == P("a/b/c/d")
    pp = p.joinpath(P("c"))
    assert pp == P("a/b/c")
    pp = p.joinpath("/c")
    assert pp == P("/c")


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
def test_div(pure_path_cls):
    P = pure_path_cls
    p = P("a/b")
    pp = p / "c"
    assert pp == P("a/b/c")
    assert type(pp) == type(p)
    pp = p / "c/d"
    assert pp == P("a/b/c/d")
    pp = p / "c" / "d"
    assert pp == P("a/b/c/d")
    pp = "c" / p / "d"
    assert pp == P("c/a/b/d")
    pp = p / P("c")
    assert pp == P("a/b/c")
    pp = p / "/c"
    assert pp == P("/c")


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
@pytest.mark.parametrize(
    ["pathstr"], [("a",), ("a/b",), ("a/b/c",), ("/",), ("/a/b",), ("/a/b/c",)]
)
def test_str(check_str, pure_path_cls, pathstr):
    check_str(pure_path_cls, pathstr, (pathstr,))
    check_str(pure_path_cls, ".", ("",))


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
@pytest.mark.parametrize(
    ["pathstr"], [("a",), ("a/b",), ("a/b/c",), ("/",), ("/a/b",), ("/a/b/c",)]
)
def test_as_posix(pure_path_cls, pathstr):
    P = pure_path_cls
    assert P(pathstr).as_posix() == pathstr


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
def test_as_bytes(pure_path_cls):
    sep = os.fsencode(pure_path_cls._flavour.sep)
    P = pure_path_cls
    assert bytes(P("a/b")) == b"a" + sep + b"b"


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
@pytest.mark.parametrize(["pathstr"], [("a",), ("",)])
@pytest.mark.xfail(raises=ValueError)
def test_as_uri_failed(pure_path_cls, pathstr):
    P = pure_path_cls
    P(pathstr).as_uri()


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
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


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
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


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
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


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
def test_match(pure_path_cls):
    P = pure_path_cls
    # Simple relative pattern.
    assert P("b.py").match("b.py")
    assert P("a/b.py").match("b.py")
    assert P("/a/b.py").match("b.py")
    assert not (P("a.py").match("b.py"))
    assert not (P("b/py").match("b.py"))
    assert not (P("/a.py").match("b.py"))
    assert not (P("b.py/c").match("b.py"))
    # Wilcard relative pattern.
    assert P("b.py").match("*.py")
    assert P("a/b.py").match("*.py")
    assert P("/a/b.py").match("*.py")
    assert not (P("b.pyc").match("*.py"))
    assert not (P("b./py").match("*.py"))
    assert not (P("b.py/c").match("*.py"))
    # Multi-part relative pattern.
    assert P("ab/c.py").match("a*/*.py")
    assert P("/d/ab/c.py").match("a*/*.py")
    assert not (P("a.py").match("a*/*.py"))
    assert not (P("/dab/c.py").match("a*/*.py"))
    assert not (P("ab/c.py/d").match("a*/*.py"))
    # Absolute pattern.
    assert P("/b.py").match("/*.py")
    assert not (P("b.py").match("/*.py"))
    assert not (P("a/b.py").match("/*.py"))
    assert not (P("/a/b.py").match("/*.py"))
    # Multi-part absolute pattern.
    assert P("/a/b.py").match("/a/*.py")
    assert not (P("/ab.py").match("/a/*.py"))
    assert not (P("/a/b/c.py").match("/a/*.py"))
    # Multi-part glob-style pattern.
    assert not (P("/a/b/c.py").match("/**/*.py"))
    assert P("/a/b/c.py").match("/a/**/*.py")


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
def test_ordering(pure_path_cls):
    P = pure_path_cls
    a = P("a")
    b = P("a/b")
    c = P("abc")
    d = P("b")
    assert a < b
    assert a < c
    assert a < d
    assert b < c
    assert c < d
    a = P("/a")
    b = P("/a/b")
    c = P("/abc")
    d = P("/b")
    assert a < b
    assert a < c
    assert a < d
    assert b < c
    assert c < d
    with pytest.raises(TypeError):
        P() < {}


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
def test_parts(pure_path_cls):
    # `parts` returns a tuple.
    P = pure_path_cls
    sep = P._flavour.sep
    p = P("a/b")
    parts = p.parts
    assert parts == ("a", "b")
    # The object gets reused.
    assert parts is p.parts
    # When the path is absolute, the anchor is a separate part.
    p = P("/a/b")
    parts = p.parts
    assert parts == (sep, "a", "b")


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
def test_fspath(check_str, pure_path_cls):
    P = pure_path_cls
    p = P("a/b")
    check_str(P, p.__fspath__(), ("a/b",))
    check_str(P, os.fspath(p), ("a/b",))


@pytest.mark.parametrize(["pure_path_cls"], [(PureHttpPath,)])
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
def test_parent(pure_path_cls):
    # Relative
    P = pure_path_cls
    p = P("a/b/c")
    assert p.parent == P("a/b")
    assert p.parent.parent == P("a")
    assert p.parent.parent.parent == P()
    assert p.parent.parent.parent.parent == P()
    # Anchored
    p = P("/a/b/c")
    assert p.parent == P("/a/b")
    assert p.parent.parent == P("/a")
    assert p.parent.parent.parent == P("/")
    assert p.parent.parent.parent.parent == P("/")


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
def test_drive(pure_path_cls):
    P = pure_path_cls
    assert P("a/b").drive == ""
    assert P("/a/b").drive == ""
    assert P("").drive == ""


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_root(pure_path_cls):
    P = pure_path_cls
    sep = pure_path_cls._flavour.sep
    assert P("").root == ""
    assert P("a/b").root == ""
    assert P("/").root == sep
    assert P("/a/b").root == sep


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_anchor(pure_path_cls):
    P = pure_path_cls
    sep = pure_path_cls._flavour.sep
    assert P("").anchor == ""
    assert P("a/b").anchor == ""
    assert P("/").anchor == sep
    assert P("/a/b").anchor == sep


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_name(pure_path_cls):
    P = pure_path_cls
    assert P("").name == ""
    assert P(".").name == ""
    assert P("/").name == ""
    assert P("a/b").name == "b"
    assert P("/a/b").name == "b"
    assert P("/a/b/.").name == "b"
    assert P("a/b.py").name == "b.py"
    assert P("/a/b.py").name == "b.py"


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_suffix(pure_path_cls):
    P = pure_path_cls
    assert P("").suffix == ""
    assert P(".").suffix == ""
    assert P("..").suffix == ""
    assert P("/").suffix == ""
    assert P("a/b").suffix == ""
    assert P("/a/b").suffix == ""
    assert P("/a/b/.").suffix == ""
    assert P("a/b.py").suffix == ".py"
    assert P("/a/b.py").suffix == ".py"
    assert P("a/.hgrc").suffix == ""
    assert P("/a/.hgrc").suffix == ""
    assert P("a/.hg.rc").suffix == ".rc"
    assert P("/a/.hg.rc").suffix == ".rc"
    assert P("a/b.tar.gz").suffix == ".gz"
    assert P("/a/b.tar.gz").suffix == ".gz"
    assert P("a/Some name. Ending with a dot.").suffix == ""
    assert P("/a/Some name. Ending with a dot.").suffix == ""


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_suffixes(pure_path_cls):
    P = pure_path_cls
    assert P("").suffixes == []
    assert P(".").suffixes == []
    assert P("/").suffixes == []
    assert P("a/b").suffixes == []
    assert P("/a/b").suffixes == []
    assert P("/a/b/.").suffixes == []
    assert P("a/b.py").suffixes == [".py"]
    assert P("/a/b.py").suffixes == [".py"]
    assert P("a/.hgrc").suffixes == []
    assert P("/a/.hgrc").suffixes == []
    assert P("a/.hg.rc").suffixes == [".rc"]
    assert P("/a/.hg.rc").suffixes == [".rc"]
    assert P("a/b.tar.gz").suffixes == [".tar", ".gz"]
    assert P("/a/b.tar.gz").suffixes == [".tar", ".gz"]
    assert P("a/Some name. Ending with a dot.").suffixes == []
    assert P("/a/Some name. Ending with a dot.").suffixes == []


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_stem(pure_path_cls):
    P = pure_path_cls
    assert P("").stem == ""
    assert P(".").stem == ""
    assert P("..").stem == ".."
    assert P("/").stem == ""
    assert P("a/b").stem == "b"
    assert P("a/b.py").stem == "b"
    assert P("a/.hgrc").stem == ".hgrc"
    assert P("a/.hg.rc").stem == ".hg"
    assert P("a/b.tar.gz").stem == "b.tar"
    assert P("a/Some name. Ending with a dot.").stem == "Some name. Ending with a dot."


@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_with_name(pure_path_cls):
    P = pure_path_cls
    assert P("a/b").with_name("d.xml") == P("a/d.xml")
    assert P("/a/b").with_name("d.xml") == P("/a/d.xml")
    assert P("a/b.py").with_name("d.xml") == P("a/d.xml")
    assert P("/a/b.py").with_name("d.xml") == P("/a/d.xml")
    assert P("a/Dot ending.").with_name("d.xml") == P("a/d.xml")
    assert P("/a/Dot ending.").with_name("d.xml") == P("/a/d.xml")


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
def test_with_stem(pure_path_cls):
    P = pure_path_cls
    assert P("a/b").with_stem("d") == P("a/d")
    assert P("/a/b").with_stem("d") == P("/a/d")
    assert P("a/b.py").with_stem("d") == P("a/d.py")
    assert P("/a/b.py").with_stem("d") == P("/a/d.py")
    assert P("/a/b.tar.gz").with_stem("d") == P("/a/d.gz")
    assert P("a/Dot ending.").with_stem("d") == P("a/d")
    assert P("/a/Dot ending.").with_stem("d") == P("/a/d")


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
def test_with_suffix(pure_path_cls):
    P = pure_path_cls
    assert P("a/b").with_suffix(".gz") == P("a/b.gz")
    assert P("/a/b").with_suffix(".gz") == P("/a/b.gz")
    assert P("a/b.py").with_suffix(".gz") == P("a/b.gz")
    assert P("/a/b.py").with_suffix(".gz") == P("/a/b.gz")
    assert P("a/b.py").with_suffix("") == P("a/b")
    assert P("/a/b").with_suffix("") == P("/a/b")


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
@pytest.mark.xfail(raises=NotImplementedError)
def test_relative_to_fail(pure_path_cls):
    pure_path_cls().relative_to(pure_path_cls("a"))

@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_is_relative_to(pure_path_cls):
    assert not pure_path_cls().is_relative_to(pure_path_cls("a"))

@pytest.mark.parametrize(["pure_path_cls"], pure_path_classes)
def test_pickling_common(pure_path_cls):
    P = pure_path_cls
    p = P('/a/b')
    for proto in range(0, pickle.HIGHEST_PROTOCOL + 1):
        dumped = pickle.dumps(p, proto)
        pp = pickle.loads(dumped)
        assert pp.__class__ is p.__class__
        assert pp == p
        assert hash(pp) == hash(p)
        assert str(pp) == str(p)
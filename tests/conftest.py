import pytest


@pytest.fixture
def check_parse_parts():
    def _f(flavour, arg, expected):
        f = flavour.parse_parts
        sep = flavour.sep
        altsep = flavour.altsep
        actual = f([x.replace("/", sep) for x in arg])

        assert actual == expected
        if altsep:
            actual = f([x.replace("/", altsep) for x in arg])
            assert actual == expected

    return _f


@pytest.fixture
def check_str_subclass():
    def _f(cls, *args):
        class StrSubclass(str):
            pass

        P = cls
        p = P(*(StrSubclass(x) for x in args))
        assert p == P(*args)
        for part in p.parts:
            assert type(part) is str

    return _f


@pytest.fixture
def check_str():
    def _f(cls, expected, args):
        p = cls(*args)
        assert str(p) == expected.replace("/", cls._flavour.sep)
    return _f
import boto3
import pytest
from moto import mock_s3

import paaaaath


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


@pytest.fixture
def s3bucket():
    class S3Bucket:
        def __init__(self, name):
            self.name = name
            self._client = boto3.client("s3", region_name="us-east-1")
            self._client.create_bucket(Bucket=name)

        def put(self, key, content):
            self._client.put_object(Bucket=self.name, Body=content, Key=key)

        def get(self, key):
            print(self.name, key)
            return self._client.get_object(Bucket=self.name, Key=key)

        def touch(self, key):
            self._client.put_object(Bucket=self.name, Key=key)

        def head(self, key):
            return self._client.head_object(Bucket=self.name, Key=key)

        @property
        def root(self):
            return f"s3://{self.name}/"

    with mock_s3():
        # To connect with moto, recreate S3 client
        paaaaath.s3.S3Path._client = boto3.client(
            "s3"
        )  # low-level client is thread safe
        yield S3Bucket("test")

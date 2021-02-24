from abc import ABC

import random
import boto3
import pytest
from moto import mock_s3
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage


import paaaaath


class Bucket(ABC):
    def put(self, key, content):
        ...

    def get(self, key):
        ...

    @property
    def root(self):
        ...


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
def gcsbucket():
    class GCSBucket(Bucket):
        def __init__(self, name):
            self.name = name
            self._client = storage.Client(
                credentials=AnonymousCredentials(),
                client_options={"api_endpoint": "http://127.0.0.1:4443"},
            )
            self._client.create_bucket(name)

        def put(self, key, content=b""):
            self._client.get_bucket(self.name).blob(key).upload_from_string(content)

        def get(self, key):
            return self._client.get_bucket(self.name).get_blob(key)

        @property
        def root(self):
            return f"gs://{self.name}/"

        # To connect with fake-gcs-server, recreate gcs client
        paaaaath.gcs.GCSPath._client = storage.Client(
            credentials=AnonymousCredentials(),
            client_options={"api_endpoint": "http://127.0.0.1:4443"},
        )

    bucket = "".join([random.choice("0123456789abcdefghijklmnopqrstuvwxyz") for _ in range(32)])
    yield GCSBucket(bucket)


@pytest.fixture
def s3bucket():
    class S3Bucket(Bucket):
        def __init__(self, name):
            self.name = name
            self._client = boto3.client("s3", region_name="us-east-1")
            self._client.create_bucket(Bucket=name)

        def put(self, key, content=b""):
            self._client.put_object(Bucket=self.name, Body=content, Key=key)

        def get(self, key):
            return self._client.get_object(Bucket=self.name, Key=key)

        @property
        def root(self):
            return f"s3://{self.name}/"

    with mock_s3():
        # To connect with moto, recreate S3 client
        paaaaath.s3.S3Path._client = boto3.client(
            "s3"
        )  # low-level client is thread safe
        yield S3Bucket("test")
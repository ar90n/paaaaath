import pytest
from paaaaath.gcs import GCSPath, PureGCSPath, _gcs_flavour
from paaaaath.s3 import PureS3Path, S3Path, _s3_flavour


@pytest.mark.parametrize(
    ["flavour", "uri_str", "expect"],
    [
        (
            _s3_flavour,
            ["s3://bucket/foo/bar"],
            ("s3://bucket", "/", ["s3://bucket/", "foo", "bar"]),
        ),
        (
            _gcs_flavour,
            ["gs://bucket/foo/bar/"],
            ("gs://bucket", "/", ["gs://bucket/", "foo", "bar"]),
        ),
    ],
)
def test_flavour_check_parse_parts(check_parse_parts, flavour, uri_str, expect):
    check_parse_parts(flavour, uri_str, expect)


@pytest.mark.parametrize(
    ["splitroot", "uri_str", "expect"],
    [
        (_s3_flavour.splitroot, "s3://bucket/foo/bar", ("s3://bucket", "/", "foo/bar")),
        (
            _gcs_flavour.splitroot,
            "gs://bucket/foo/bar",
            ("gs://bucket", "/", "foo/bar"),
        ),
    ],
)
def test_flavour_splitroot(splitroot, uri_str, expect):
    assert splitroot(uri_str) == expect


@pytest.mark.parametrize(
    ["cls", "uri"],
    [
        (
            S3Path,
            "http://example.com",
        ),
        (
            S3Path,
            "gs://example.com",
        ),
        (
            GCSPath,
            "http://example.com",
        ),
        (
            GCSPath,
            "s3://example.com",
        ),
    ],
)
def test_create_path_fail(cls, uri):
    with pytest.raises(ValueError):
        cls(uri)


@pytest.mark.parametrize(["cls", "scheme"], [(S3Path, "s3"), (GCSPath, "gs")])
@pytest.mark.parametrize(
    ["uri", "bucket", "key"],
    [
        ("{}://bucket/key", "bucket", "key"),
        ("{}://bucket/parent/key", "bucket", "parent/key"),
        ("/bucket/key", "", "bucket/key"),
    ],
)
def test_bucket_key(cls, scheme, uri, bucket, key):
    p = cls(uri.format(scheme))
    assert p.bucket == bucket
    assert p.key == key


@pytest.mark.parametrize(
    ["cls", "pure_cls", "scheme"],
    [(S3Path, PureS3Path, "s3"), (GCSPath, PureGCSPath, "gs")],
)
@pytest.mark.parametrize(
    ["uri", "resolve"],
    [
        (
            "{}://example.com",
            "{}://example.com/",
        ),
        (
            "{}://user@example.com:80/foo/bar/piyo/../fuz",
            "{}://user@example.com:80/foo/bar/fuz",
        ),
    ],
)
def test_path_resolve(cls, pure_cls, scheme, uri, resolve):
    p = cls(uri.format(scheme))
    expect = pure_cls(resolve.format(scheme))

    assert p.resolve() == expect


@pytest.mark.parametrize(["cls"], [(S3Path,), (GCSPath,)])
@pytest.mark.xfail(raises=NotImplementedError)
def test_gethome_fail(cls):
    cls.home()


@pytest.mark.parametrize(["cls", "scheme"], [(S3Path, "s3"), (GCSPath, "gs")])
@pytest.mark.xfail(raises=NotImplementedError)
def test_samefile_fail(cls, scheme):
    uri = f"{scheme}://example/a"
    cls(uri).samefile(cls(uri))

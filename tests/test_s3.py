import collections
import io
import time
from os import rmdir

import pytest

from paaaaath import PureS3Path, S3Path
from paaaaath.s3 import _s3_flavour


@pytest.mark.parametrize(
    ["partsstr", "expect"],
    [
        (
            ["s3://example.com:80"],
            ("s3://example.com:80", "/", ["s3://example.com:80/"]),
        ),
    ],
)
def test_s3_flavour_check_parse_parts(check_parse_parts, partsstr, expect):
    flavour = _s3_flavour
    check_parse_parts(flavour, partsstr, expect)


@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("s3://example.com", ("s3://example.com", "/", "")),
    ],
)
def test_s3_flavour_splitroot(pathstr, expect):
    f = _s3_flavour.splitroot
    assert f(pathstr) == expect


@pytest.mark.parametrize(
    ["uri"],
    [
        ("http://example.com",),
    ],
)
@pytest.mark.xfail(raises=ValueError)
def test_create_path_fail(uri):
    S3Path(uri)


@pytest.mark.parametrize(
    ["uri", "bucket", "key"],
    [
        ("s3://bucket/key", "bucket", "key"),
        ("s3://bucket/parent/key", "bucket", "parent/key"),
        ("/bucket/key", "", "bucket/key"),
    ],
)
def test_bucket_key(uri, bucket, key):
    p = S3Path(uri)
    assert p.bucket == bucket
    assert p.key == key


@pytest.mark.parametrize(
    ["uri", "resolve"],
    [
        (
            "s3://example.com",
            PureS3Path("s3://example.com/"),
        ),
        (
            "s3://user@example.com:80/foo/bar/piyo/../fuz",
            PureS3Path("s3://user@example.com:80/foo/bar/fuz"),
        ),
    ],
)
def test_s3_path_resolve(uri, resolve):
    path = S3Path(uri)

    assert path.resolve() == resolve


@pytest.mark.xfail(raises=NotImplementedError)
def test_gethome_fail():
    S3Path.home()


@pytest.mark.xfail(raises=NotImplementedError)
def test_samefile_fail():
    S3Path("s3://example/a").samefile(S3Path("s3://example/a"))


@pytest.mark.parametrize(
    ["putstr", "pathstr", "expect"],
    [
        ("foo", "foo", True),
        ("foo/", "foo", True),
        ("foo", "foo/", True),
        ("foo/", "foo/", True),
        ("foo", "bar", False),
    ],
)
def test_exists(s3bucket, putstr, pathstr, expect):
    s3bucket.touch(putstr)
    assert S3Path(f"{s3bucket.root}{pathstr}").exists() == expect


@pytest.mark.parametrize(
    ["rmode", "wmode", "file_cls", "expect"],
    [
        ("r", "w", io.TextIOBase, "this is file A"),
        ("rb", "wb", io.BufferedIOBase, b"this is file A"),
    ],
)
def test_open(s3bucket, rmode, wmode, file_cls, expect):
    p = S3Path(f"{s3bucket.root}/file")
    with p.open(wmode) as fw:
        assert isinstance(fw, file_cls)
        fw.write(expect)
    with p.open(rmode) as fr:
        assert isinstance(fr, file_cls)
        assert fr.read() == expect


@pytest.mark.parametrize(
    ["expect"],
    [
        ("abcdefg",),
    ],
)
def test_read_write_text(s3bucket, expect):
    url = f"{s3bucket.root}/file"
    S3Path(url).write_text(expect)
    assert S3Path(url).read_text() == expect


@pytest.mark.parametrize(
    ["expect"],
    [
        (b"abcdefg",),
    ],
)
def test_read_write_bytes(s3bucket, expect):
    url = f"{s3bucket.root}/file"
    S3Path(url).write_bytes(expect)
    assert S3Path(url).read_bytes() == expect


@pytest.mark.parametrize(
    ["keys", "root", "expect"],
    [
        (("a", "b", "c"), "/", {"a", "b", "c"}),
        (("a", "b/b", "b/c", "c/d"), "/b", {"b/b", "b/c"}),
        (("a", "b/b", "b/c", "c/d/e", "c/f/g"), "/c", {"c/d", "c/f"}),
        (("a/", "b/b", "b/c", "c/d"), "/a", {}),
        ([str(i) for i in range(1024)], "/", {str(i) for i in range(1024)}),
    ],
)
def test_iterdir(s3bucket, keys, root, expect):
    for k in keys:
        s3bucket.touch(k)
    it = S3Path(f"{s3bucket.root}/{root}").iterdir()
    assert isinstance(it, collections.Iterable)
    assert set(it) == {S3Path(f"{s3bucket.root}/{p}") for p in expect}


@pytest.mark.parametrize(
    ["contents", "key", "expect"],
    [
        ({"a": "abc"}, "b", {"a": "abc", "b": ""}),
    ],
)
def test_touch(s3bucket, contents, key, expect):
    for k, v in contents.items():
        s3bucket.put(k, v)
    S3Path(f"{s3bucket.root}/{key}").touch()

    for k, v in expect.items():
        assert s3bucket.get(k)["Body"].read().decode("utf-8") == v


@pytest.mark.parametrize(
    ["contents"],
    [
        ({"a": "abc"},),
    ],
)
def test_touch_exist_ok(s3bucket, contents):
    originals = {}
    for k, v in contents.items():
        s3bucket.put(k, v)
        originals[k] = s3bucket.get(k)

    time.sleep(1)

    for k, v in contents.items():
        S3Path(f"{s3bucket.root}/{k}").touch(exist_ok=True)

    for k, org in originals.items():
        touched = s3bucket.get(k)
        assert org["ETag"] == touched["ETag"]
        assert org["LastModified"] < touched["LastModified"]


@pytest.mark.parametrize(
    ["key", "args", "expect"],
    [("a/b", {}, FileNotFoundError), ("exist", {"exist_ok": False}, FileExistsError)],
)
def test_touch_fail(s3bucket, key, args, expect):
    s3bucket.touch("exist")
    with pytest.raises(expect):
        S3Path(f"{s3bucket.root}/{key}").touch(**args)


@pytest.mark.parametrize(
    ["key", "args"],
    [
        ("a", {}),
        ("a/", {}),
        ("parent/a/b/c", {"parents": True}),
        ("parent", {"exist_ok": True}),
    ],
)
def test_mkdir(s3bucket, key, args):
    s3bucket.touch("parent/")
    S3Path(f"{s3bucket.root}/{key}").mkdir(**args)
    assert s3bucket.get(f"{key.rstrip('/')}/")


@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("parent", OSError),
        ("parent/a/b/c", FileNotFoundError),
    ],
)
def test_mkdir_fail(s3bucket, pathstr, expect):
    s3bucket.touch("parent/")
    with pytest.raises(expect):
        S3Path(f"{s3bucket.root}/{pathstr}").mkdir()


@pytest.mark.parametrize(
    ["key", "content", "expect"],
    [
        ("key", "", False),
        ("key/", "", True),
        ("key/", "abc", False),
        ("key/file", "", False),
        ("key/dir/", "", True),
    ],
)
def test_is_dir(s3bucket, key, content, expect):
    s3bucket.put(key, content)
    assert S3Path(f"{s3bucket.root}/{key}").is_dir() == expect


@pytest.mark.parametrize(
    ["api_name", "args"],
    [
        ("home", []),
        ("samefile", [S3Path("s3://other/abc")]),
        ("glob", ["*.py"]),
        ("rglob", ["*.py"]),
        ("absolute", []),
        ("stat", []),
        ("owner", []),
        ("readlink", []),
        ("chmod", [0x666]),
        ("lchmod", [0x666]),
        ("unlink", []),
        ("rmdir", []),
        ("lstat", []),
        ("link_to", [S3Path("s3://tmp")]),
        ("rename", [S3Path("s3://tmp")]),
        ("replace", [S3Path("s3://tmp")]),
        ("symlink_to", [S3Path("s3://tmp")]),
        ("is_file", []),
        ("expanduser", []),
    ],
)
@pytest.mark.xfail(raises=NotImplementedError)
def test_path_public_api_fail(api_name, args):
    getattr(S3Path("s3://example/"), api_name)(*args)


@pytest.mark.parametrize(
    ["api_name"],
    [
        ("is_mount",),
        ("is_symlink",),
        ("is_block_device",),
        ("is_char_device",),
        ("is_fifo",),
        ("is_socket",),
    ],
)
def test_path_predicate(api_name):
    assert getattr(S3Path("s3://example/com"), api_name)() == False

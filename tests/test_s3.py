import collections
import io
import time
import sys

import pytest
from paaaaath import S3Path


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
    s3bucket.put(putstr)
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
        (("a", "b/e", "b/c", "c/d"), "/b/", {"b/e", "b/c"}),
        (("a", "b/b", "b/c", "c/d/e", "c/f/g"), "/c", {"c/d", "c/f"}),
        (("a/", "b/b", "b/c", "c/d"), "a/", {}),
        (("a/b/", "b/b", "b/c", "c/d"), "a/b", {}),
        (("a/b/", "b/b", "b/c", "c/d"), "/a/b", {}),
        ([str(i) for i in range(1024)], "/", {str(i) for i in range(1024)}),
    ],
)
def test_iterdir(s3bucket, keys, root, expect):
    for k in keys:
        s3bucket.put(k)
    it = S3Path(f"{s3bucket.root}/{root}").iterdir()
    assert isinstance(it, collections.abc.Iterable)
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
    S3Path(f"{s3bucket.root}/{key}").touch(exist_ok=False)

    for k, v in expect.items():
        assert s3bucket.get(k)["Body"].read().decode("utf-8") == v


@pytest.mark.skip("exist_ok doesn't work with minio")
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
    s3bucket.put("exist")
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
    s3bucket.put("parent/")
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
    s3bucket.put("parent/")
    with pytest.raises(expect):
        S3Path(f"{s3bucket.root}/{pathstr}").mkdir()


@pytest.mark.parametrize(
    ["key", "content", "expect"],
    [
        ("key", "", False),
        ("key/", "", True),
        pytest.param("key/a", "", True, marks=pytest.mark.skip(reason="minio doesn't support directories")),
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
        pytest.param(
            "stat",
            [],
            marks=pytest.mark.skipif(
                (3, 10) <= sys.version_info,
                reason="python 3.10 require stat implementation",
            ),
        ),
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

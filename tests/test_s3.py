import collections
import io
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
    S3Path().samefile(S3Path())


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
        (("a", "b/b", "b/c", "c/d/e"), "/c", {"c/d"}),
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


@pytest.mark.xfail(raises=NotImplementedError)
def test_glob_fail():
    S3Path().glob("")


@pytest.mark.xfail(raises=NotImplementedError)
def test_rglob_fail():
    S3Path().rglob("")


@pytest.mark.xfail(raises=NotImplementedError)
def test_chmod_fail():
    S3Path().chmod(0o777)


@pytest.mark.xfail(raises=NotImplementedError)
def test_stat_fail():
    S3Path().stat()


@pytest.mark.parametrize(
    ["pathstr"],
    [
        ("a",),
        ("a/b",),
    ],
)
def test_unlink(s3bucket, pathstr):
    s3bucket.touch(pathstr)
    path = S3Path(f"{s3bucket.root}/{pathstr}")
    path.unlink()
    assert not path.exists()


@pytest.mark.parametrize(
    ["touchkey", "pathstr", "expect"],
    [
        ("a/", "a/", PermissionError),
        ("a", "b", FileNotFoundError),
    ],
)
def test_unlink_fail(s3bucket, touchkey, pathstr, expect):
    s3bucket.touch(touchkey)
    path = S3Path(f"{s3bucket.root}/{pathstr}")
    with pytest.raises(expect):
        path.unlink()


@pytest.mark.parametrize(
    ["touch_keys", "rmdir_key", "exist_keys", "non_exist_keys"],
    [
        (["a/"], "a/", [], ["a/"]),
        (["a/"], "a", [], ["a/"]),
        (["a/b/"], "a/b/", [], ["a/b/"]),
        (["a/b", "a/c", "d/"], "a/", ["d/"], ["a/b", "a/c"]),
    ],
)
def test_rmdir(s3bucket, touch_keys, rmdir_key, exist_keys, non_exist_keys):
    for k in touch_keys:
        s3bucket.touch(k)
    S3Path(f"{s3bucket.root}/{rmdir_key}").rmdir()

    for k in exist_keys:
        assert S3Path(f"{s3bucket.root}/{k}").exists()

    for k in non_exist_keys:
        assert not S3Path(f"{s3bucket.root}/{k}").exists()


@pytest.mark.parametrize(
    ["touch_key", "rmdir_key", "expect"],
    [
        ("a", "a", NotADirectoryError),
        ("a", "b", FileNotFoundError),
    ],
)
def test_rmdir_fail(s3bucket, touch_key, rmdir_key, expect):
    s3bucket.touch(touch_key)
    path = S3Path(f"{s3bucket.root}/{rmdir_key}")
    with pytest.raises(expect):
        path.rmdir()


@pytest.mark.xfail(raises=NotImplementedError)
def test_rename_fail():
    S3Path().rename("")


@pytest.mark.xfail(raises=NotImplementedError)
def test_lstat_fail():
    S3Path().lstat()


@pytest.mark.xfail(raises=NotImplementedError)
def test_link_to_fail():
    S3Path().link_to("")


@pytest.mark.xfail(raises=NotImplementedError)
def test_replace_fail():
    S3Path().replace("")


@pytest.mark.parametrize(
    ["keys", "name", "expect"],
    [
        (("a",), "b", {"a", "b", "c"}),
    ],
)
def test_touch(s3bucket, keys, name, expect):
    for k in keys:
        s3bucket.touch(k)
    S3Path(f"{s3bucket.root}/{name}").touch()


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
    ["putstr", "pathstr", "expect"],
    [
        ("foo", "foo", False),
        ("foo/", "foo", True),
        ("foo", "foo/", False),
        ("foo/", "foo/", True),
        ("foo", "bar", False),
    ],
)
def test_is_dir(s3bucket, putstr, pathstr, expect):
    s3bucket.touch(putstr)
    assert S3Path(f"{s3bucket.root}{pathstr}").is_dir() == expect


@pytest.mark.parametrize(
    ["putstr", "pathstr", "expect"],
    [
        ("foo", "foo", True),
        ("foo/", "foo", False),
        ("foo", "foo/", True),
        ("foo/", "foo/", False),
        ("foo", "bar", False),
    ],
)
def test_is_file(s3bucket, putstr, pathstr, expect):
    s3bucket.touch(putstr)
    assert S3Path(f"{s3bucket.root}{pathstr}").is_file() == expect


@pytest.mark.xfail(raises=NotImplementedError)
def test_is_mount_fail():
    S3Path().is_mount()


@pytest.mark.xfail(raises=NotImplementedError)
def test_is_symlink_fail():
    S3Path().is_symlink()


@pytest.mark.xfail(raises=NotImplementedError)
def test_absolute_fail():
    S3Path().absolute()


@pytest.mark.xfail(raises=NotImplementedError)
def test_owner():
    S3Path().owner()


@pytest.mark.xfail(raises=NotImplementedError)
def test_group_fail():
    S3Path().group()


@pytest.mark.xfail(raises=NotImplementedError)
def readlink():
    S3Path().readlink()


@pytest.mark.xfail(raises=NotImplementedError)
def test_lchmod_fail():
    S3Path().lchmod(0)


@pytest.mark.xfail(raises=NotImplementedError)
def test_lstat_fail():
    S3Path().lstat()


@pytest.mark.xfail(raises=NotImplementedError)
def test_symlink_to_fail():
    S3Path().symlink_to(S3Path())


def test_is_block_device():
    assert not S3Path().is_block_device()


def test_is_char_device():
    assert not S3Path().is_char_device()


def test_is_fifo():
    assert not S3Path().is_fifo()


def test_is_socket():
    assert not S3Path().is_socket()


@pytest.mark.xfail(raises=NotImplementedError)
def expanduser():
    S3Path().expanduser()
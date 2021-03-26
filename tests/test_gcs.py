import collections
import io
import time

import pytest
from paaaaath import GCSPath


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
def test_exists(gcsbucket, putstr, pathstr, expect):
    gcsbucket.put(putstr)
    assert GCSPath(f"{gcsbucket.root}{pathstr}").exists() == expect


@pytest.mark.parametrize(
    ["rmode", "wmode", "file_cls", "expect"],
    [
        ("r", "w", io.TextIOBase, "this is file A"),
        ("rb", "wb", io.BufferedIOBase, b"this is file A"),
    ],
)
def test_open(gcsbucket, rmode, wmode, file_cls, expect):
    p = GCSPath(f"{gcsbucket.root}/file")
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
def test_read_write_text(gcsbucket, expect):
    url = f"{gcsbucket.root}/file"
    GCSPath(url).write_text(expect)
    assert GCSPath(url).read_text() == expect


@pytest.mark.parametrize(
    ["expect"],
    [
        (b"abcdefg",),
    ],
)
def test_read_write_bytes(gcsbucket, expect):
    url = f"{gcsbucket.root}/file"
    GCSPath(url).write_bytes(expect)
    assert GCSPath(url).read_bytes() == expect


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
def test_iterdir(gcsbucket, keys, root, expect):
    for k in keys:
        gcsbucket.put(k)
    it = GCSPath(f"{gcsbucket.root}/{root}").iterdir()
    assert isinstance(it, collections.Iterable)
    assert set(it) == {GCSPath(f"{gcsbucket.root}/{p}") for p in expect}


@pytest.mark.parametrize(
    ["contents", "key", "expect"],
    [
        ({"a": "abc"}, "b", {"a": "abc", "b": ""}),
    ],
)
def test_touch(gcsbucket, contents, key, expect):
    for k, v in contents.items():
        gcsbucket.put(k, v)
    GCSPath(f"{gcsbucket.root}/{key}").touch(exist_ok=False)

    for k, v in expect.items():
        assert gcsbucket.get(k).download_as_string().decode("utf-8") == v


@pytest.mark.parametrize(
    ["contents"],
    [
        ({"a": "abc"},),
    ],
)
def test_touch_exist_ok(gcsbucket, contents):
    originals = {}
    for k, v in contents.items():
        gcsbucket.put(k, v)
        originals[k] = gcsbucket.get(k)

    time.sleep(1)

    for k, v in contents.items():
        GCSPath(f"{gcsbucket.root}/{k}").touch(exist_ok=True)

    for k, org in originals.items():
        touched = gcsbucket.get(k)
        assert org.etag == touched.etag
        assert org.updated < touched.updated


@pytest.mark.parametrize(
    ["key", "args", "expect"],
    [("a/b", {}, FileNotFoundError), ("exist", {"exist_ok": False}, FileExistsError)],
)
def test_touch_fail(gcsbucket, key, args, expect):
    gcsbucket.put("exist")
    with pytest.raises(expect):
        GCSPath(f"{gcsbucket.root}/{key}").touch(**args)


@pytest.mark.parametrize(
    ["key", "args"],
    [
        ("a", {}),
        ("a/", {}),
        ("parent/a/b/c", {"parents": True}),
        ("parent", {"exist_ok": True}),
    ],
)
def test_mkdir(gcsbucket, key, args):
    gcsbucket.put("parent/")
    GCSPath(f"{gcsbucket.root}/{key}").mkdir(**args)
    assert gcsbucket.get(f"{key.rstrip('/')}/")


@pytest.mark.parametrize(
    ["pathstr", "expect"],
    [
        ("parent", OSError),
        ("parent/a/b/c", FileNotFoundError),
    ],
)
def test_mkdir_fail(gcsbucket, pathstr, expect):
    gcsbucket.put("parent/")
    with pytest.raises(expect):
        GCSPath(f"{gcsbucket.root}/{pathstr}").mkdir()


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
def test_is_dir(gcsbucket, key, content, expect):
    gcsbucket.put(key, content)
    assert GCSPath(f"{gcsbucket.root}/{key}").is_dir() == expect


@pytest.mark.parametrize(
    ["api_name", "args"],
    [
        ("home", []),
        ("samefile", [GCSPath("gs://other/abc")]),
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
        ("link_to", [GCSPath("gs://tmp")]),
        ("rename", [GCSPath("gs://tmp")]),
        ("replace", [GCSPath("gs://tmp")]),
        ("symlink_to", [GCSPath("gs://tmp")]),
        ("is_file", []),
        ("expanduser", []),
    ],
)
@pytest.mark.xfail(raises=NotImplementedError)
def test_path_public_api_fail(api_name, args):
    getattr(GCSPath("gs://example/"), api_name)(*args)


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
    assert getattr(GCSPath("gs://example/com"), api_name)() == False

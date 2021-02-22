import fnmatch
import pathlib
import posixpath
import re
from os import fsencode
from urllib.parse import quote_from_bytes, urlparse

from .common import PurePath, Path


class _UriFlavour(pathlib._Flavour):
    sep = "/"
    altsep = ""
    has_drv = True
    pathmod = type("fakepath", (), {"normpath": lambda _, x: x})()

    is_supported = True

    def splitroot(self, part, sep=sep):
        url = urlparse(part)
        scheme = url.scheme
        netloc = url.netloc
        path = url.path

        if scheme == "" and netloc != "":
            path = f"{sep}{netloc}{sep}{path}".rstrip(sep)
            netloc = ""

        drv = f"{scheme}://{netloc}" if scheme != "" else ""
        part = path.lstrip("/")
        root = sep if drv != "" or path != part else ""
        return drv, root, part

    def casefold(self, s):
        return s

    def casefold_parts(self, parts):
        return parts

    def compile_pattern(self, pattern):
        return re.compile(fnmatch.translate(pattern)).fullmatch

    def resolve(self, path, strict=False):
        norm_path = posixpath.normpath(self.join(path.parts[1:]))
        return f"{path.drive}{path.root}{norm_path}"

    def is_reserved(self, parts):
        return False

    def make_uri(self, path):
        bpath = bytes(fsencode(self.join(path.parts[1:])))
        return f"{path.drive}{path.root}{quote_from_bytes(bpath)}"

    def gethomedir(self, username):
        raise NotImplementedError("gethomedir() not available on this system")


_uri_flavour = _UriFlavour()


class PureUriPath(PurePath):
    _flavour = _uri_flavour
    __slots__ = ()


class UriPath(Path, PureUriPath):
    __slots__ = ()

    @classmethod
    def home(cls):
        raise NotImplementedError("home() is not supported.")

    def samefile(self, other_path):
        raise NotImplementedError("samefile() is not supported.")

    def iterdir(self):
        raise NotImplementedError("iterdir() is not supported.")

    def glob(self, pattern):
        raise NotImplementedError("glob() is not supported")

    def rglob(self, pattern):
        raise NotImplementedError("rglob() is not supported")

    def absolute(self):
        raise NotImplementedError("absolute() is not supported")

    def stat(self):
        raise NotImplementedError("stat() is not supported")

    def owner(self):
        raise NotImplementedError("owner() is not supported")

    def group(self):
        raise NotImplementedError("group() is not supported")

    def open(self, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
        raise NotImplementedError("open() is not supported")

    def readlink(self):
        raise NotImplementedError("readlink() is not supported")

    def touch(self, mode=0o666, exist_ok=True):
        raise NotImplementedError("touch() is not supported")

    def _mkdir(self, mode):
        raise NotImplementedError("_mkdir() is not supported")

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        try:
            self._mkdir(mode)
        except FileNotFoundError:
            if not parents or self.parent == self:
                raise
            self.parent.mkdir(parents=True, exist_ok=True)
            self.mkdir(mode, parents=False, exist_ok=exist_ok)
        except OSError:
            if not exist_ok or not self.is_dir():
                raise

    def chmod(self, mode):
        raise NotImplementedError("chmod() is not supported")

    def lchmod(self, mode):
        raise NotImplementedError("lchmod() is not supported")

    def unlink(self, missing_ok=False):
        raise NotImplementedError("unlink() is not supported")

    def rmdir(self):
        raise NotImplementedError("rmdir() is not supported")

    def lstat(self):
        raise NotImplementedError("lstat() is not supported")

    def link_to(self, target):
        raise NotImplementedError("link_to() is not supported")

    def rename(self, target):
        raise NotImplementedError("rename() is not supported")

    def replace(self, target):
        raise NotImplementedError("replace() is not supported")

    def symlink_to(self, target, target_is_directory=False):
        raise NotImplementedError("symlink_to() is not supported")

    def exists(self):
        raise NotImplementedError("exists() is not supported")

    def is_dir(self):
        raise NotImplementedError("is_dir() is not supported")

    def is_file(self):
        raise NotImplementedError("is_file() is not supported")

    def is_mount(self):
        return False

    def is_symlink(self):
        return False

    def is_block_device(self):
        return False

    def is_char_device(self):
        return False

    def is_fifo(self):
        return False

    def is_socket(self):
        return False

    def expanduser(self):
        raise NotImplementedError("expanduser() is not supported")
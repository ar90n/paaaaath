from os import fsencode, utime
import posixpath
import fnmatch
from smart_open import smart_open_lib
import re
from urllib.parse import urlparse, quote_from_bytes
import pathlib

from .basic import Path


class _HttpFlavour(pathlib._Flavour):
    sep = "/"
    altsep = ""
    has_drv = True
    pathmod = type("fakepath", (), {"normpath": lambda _, x: x})()

    is_supported = True

    def splitroot(self, part, sep=sep):
        url = urlparse(part)
        if url.scheme not in ["", "http", "https"]:
            raise ValueError(
                f"http and https are only supported. but {url.scheme} was given."
            )

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


_http_flavour = _HttpFlavour()


class PureHttpPath(pathlib.PurePath):
    _flavour = _http_flavour
    __slots__ = ()

    def relative_to(self, *other):
        raise NotImplementedError("relative_to is not implemented.")

    def is_relative_to(self, *other) -> bool:
        return False


class _HttpAccessor(pathlib._Accessor):
    utime = utime

    @staticmethod
    def open(*args, **kwargs):
        raise NotImplementedError("open() not available on this system")

    @staticmethod
    def stat(*args, **kwargs):
        raise NotImplementedError("stat() not available on this system")

    @staticmethod
    def lstat(*args, **kwargs):
        raise NotImplementedError("lstat() not available on this system")

    @staticmethod
    def listdir(*args, **kwargs):
        raise NotImplementedError("listdir() not available on this system")

    @staticmethod
    def scandir(*args, **kwargs):
        raise NotImplementedError("scandir() not available on this system")

    @staticmethod
    def chmod(*args, **kwargs):
        raise NotImplementedError("chmod() not available on this system")

    @staticmethod
    def lchmod(*args, **kwargs):
        raise NotImplementedError("lchmod() not available on this system")

    @staticmethod
    def mkdir(*args, **kwargs):
        raise NotImplementedError("mkdir() not available on this system")

    @staticmethod
    def unlink(*args, **kwargs):
        raise NotImplementedError("unlink() not available on this system")

    @staticmethod
    def link_to(*args, **kwargs):
        raise NotImplementedError("link_to() not available on this system")

    @staticmethod
    def rmdir(*args, **kwargs):
        raise NotImplementedError("rmdir() not available on this system")

    @staticmethod
    def rename(*args, **kwargs):
        raise NotImplementedError("rename() not available on this system")

    @staticmethod
    def replace(*args, **kwargs):
        raise NotImplementedError("replace() not available on this system")

    @staticmethod
    def symlink(*args, **kwargs):
        raise NotImplementedError("symlink() not available on this system")

    @staticmethod
    def readlink(*args, **kwargs):
        raise NotImplementedError("Path.readlink() is unsupported on this system")

    @staticmethod
    def owner(*args, **kwargs):
        raise NotImplementedError("Path.owner() is unsupported on this system")

    @staticmethod
    def group(*args, **kwargs):
        raise NotImplementedError("Path.group() is unsupported on this system")


_http_accessor = _HttpAccessor()


class HttpPath(Path, PureHttpPath):
    __slots__ = ()

    def _init(self, template=None):
        super()._init(template)
        self._accessor = _http_accessor

    def open(self, *args, **kwargs):
        return smart_open_lib.open(str(self), *args, **kwargs)

    def is_mount(self):
        raise NotImplementedError("Path.is_mount() is unsupported on this system")
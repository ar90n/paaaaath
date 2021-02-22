import pathlib
from os import utime

from smart_open import smart_open_lib

from .common import Path, PurePath
from .uri import _UriFlavour


class _HttpFlavour(_UriFlavour):
    def splitroot(self, part, sep=None):
        sep = self.sep if sep is None else sep
        drv, root, part = super().splitroot(part, sep)

        if not any((drv == "" or drv.startswith(p) for p in ["http", "https"])):
            raise ValueError(f"http and https are only supported. but {drv} was given.")

        return drv, root, part


_http_flavour = _HttpFlavour()


class PureHttpPath(PurePath):
    _flavour = _http_flavour
    __slots__ = ()


class _HttpAccessor(pathlib._Accessor):
    @staticmethod
    def utime(*args, **kwargs):
        raise NotImplementedError("utime() not available on this system")

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

    def exists(self):
        from requests.exceptions import HTTPError

        try:
            self.open()
        except HTTPError:
            return False
        return True

    def is_mount(self):
        raise NotImplementedError("Path.is_mount() is unsupported on this system")

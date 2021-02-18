import pathlib
from os import utime

from smart_open import smart_open_lib

from .common import Path, PurePath
from .uri import _UriFlavour


class _S3Flavour(_UriFlavour):
    def splitroot(self, part, sep=None):
        sep = self.sep if sep is None else sep
        drv, root, part = super().splitroot(part, sep)

        if not any((drv.startswith(p) for p in ["", "s3"])):
            raise ValueError(f"http and https are only supported. but {drv} was given.")

        return drv, root, part


_s3_flavour = _S3Flavour()


class PureS3Path(PurePath):
    _flavour = _s3_flavour
    __slots__ = ()


class _S3Accessor(pathlib._Accessor):
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


_s3_accessor = _S3Accessor()


class S3Path(Path, PureS3Path):
    __slots__ = ()

    def _init(self, template=None):
        super()._init(template)
        self._accessor = _s3_accessor

    def open(self, *args, **kwargs):
        return smart_open_lib.open(str(self), *args, **kwargs)

    def is_mount(self):
        raise NotImplementedError("Path.is_mount() is unsupported on this system")

import sys
import os
import pathlib
from typing import List


class PurePath(pathlib.PurePath):
    _uri_cls_repository: "List[PurePath]" = []

    def __new__(cls, *args):
        return cls._create_uri_path(args, PurePath)

    @classmethod
    def register(cls, concrete_cls):
        cls._uri_cls_repository.append(concrete_cls)
        return concrete_cls

    @classmethod
    def _create_uri_path(cls, args, base_cls):
        if cls is not base_cls:
            return cls._from_parts(args)

        for concrete_cls in reversed(cls._uri_cls_repository):
            try:
                self = concrete_cls._from_parts(args)
                if self._drv != "":
                    return self
            except ValueError:
                pass

        return cls._get_default_path_cls()._from_parts(args)

    @classmethod
    def _get_default_path_cls(cls):
        from .windows import PureWindowsPath
        from .posix import PurePosixPath

        return PureWindowsPath if os.name == "nt" else PurePosixPath


if sys.version_info < (3, 9):

    def with_stem(self, stem):
        return self.with_name(stem + self.suffix)

    setattr(PurePath, with_stem.__name__, with_stem)

    def is_relative_to(self, *other):
        try:
            self.relative_to(*other)
            return True
        except ValueError:
            return False

    setattr(PurePath, is_relative_to.__name__, is_relative_to)


class Path(PurePath, pathlib.Path):
    _uri_cls_repository: "List[PurePath]" = []

    def __new__(cls, *args, **kwargs):
        self = cls._create_uri_path(args, Path)
        if not self._flavour.is_supported:
            raise NotImplementedError(
                "cannot instantiate %r on your system" % (cls.__name__,)
            )

        self._init()
        return self

    @classmethod
    def _get_default_path_cls(cls):
        from .windows import WindowsPath
        from .posix import PosixPath

        return WindowsPath if os.name == "nt" else PosixPath


class _SkeletonAccessor(pathlib._Accessor):  # type: ignore
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
        raise NotImplementedError("readlink() is unsupported on this system")

    @staticmethod
    def owner(*args, **kwargs):
        raise NotImplementedError("owner() is unsupported on this system")

    @staticmethod
    def group(*args, **kwargs):
        raise NotImplementedError("group() is unsupported on this system")


_skeleton_accessor = _SkeletonAccessor()


class _SkeletonPath(Path):
    __slots__ = ()

    def _init(self, template=None):
        super()._init(template)
        self._accessor = _skeleton_accessor

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

import os
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Callable, List, Type, cast


@dataclass
class RegisteredPurePathClass:
    missing: bool
    cls: Type["PurePath"]


class PurePath(pathlib.PurePath):
    _uri_cls_repository: List[RegisteredPurePathClass] = []

    def __new__(cls: Type["PurePath"], *args) -> "PurePath":
        return cls._create_uri_path(args, PurePath)

    @classmethod
    def register(
        cls: Type["PurePath"], missing_deps: bool = False
    ) -> Callable[[Type["PurePath"]], Type["PurePath"]]:
        def _f(concrete_cls: Type[PurePath]) -> Type[PurePath]:
            cls._uri_cls_repository.append(
                RegisteredPurePathClass(missing_deps, concrete_cls)
            )
            return concrete_cls

        return _f

    @classmethod
    def _create_uri_path(cls: Type["PurePath"], args, base_cls) -> "PurePath":
        if cls is not base_cls:
            return cls._from_parts(args)  # type: ignore

        for registered_cls in reversed(cls._uri_cls_repository):
            try:
                self = registered_cls.cls._from_parts(args)  # type: ignore
                if self._drv != "" and not registered_cls.missing:
                    return self
            except ValueError:
                pass

        return cls._get_default_path_cls()._from_parts(args)  # type: ignore

    @classmethod
    def _get_default_path_cls(cls: Type["PurePath"]) -> Type["PurePath"]:
        from paaaaath.posix import PurePosixPath
        from paaaaath.windows import PureWindowsPath

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
    _uri_cls_repository: List[RegisteredPurePathClass] = []

    def __new__(cls: Type["Path"], *args, **kwargs) -> "Path":
        self = cast(Path, cls._create_uri_path(args, Path))
        if not self._flavour.is_supported:  # type: ignore
            raise NotImplementedError(
                "cannot instantiate %r on your system" % (cls.__name__,)
            )

        self._init()  # type: ignore
        return self

    @classmethod
    def _get_default_path_cls(cls: Type["Path"]) -> Type["Path"]:
        from paaaaath.posix import PosixPath
        from paaaaath.windows import WindowsPath

        return WindowsPath if os.name == "nt" else PosixPath


class _SkeletonAccessor(pathlib._Accessor):  # type: ignore
    @classmethod
    def utime(cls, *args, **kwargs):
        raise NotImplementedError("utime() not available on this system")

    @classmethod
    def open(cls, *args, **kwargs):
        raise NotImplementedError("open() not available on this system")

    @classmethod
    def stat(cls, *args, **kwargs):
        raise NotImplementedError("stat() not available on this system")

    @classmethod
    def lstat(cls, *args, **kwargs):
        raise NotImplementedError("lstat() not available on this system")

    @classmethod
    def listdir(cls, *args, **kwargs):
        raise NotImplementedError("listdir() not available on this system")

    @classmethod
    def scandir(cls, *args, **kwargs):
        raise NotImplementedError("scandir() not available on this system")

    @classmethod
    def chmod(cls, *args, **kwargs):
        raise NotImplementedError("chmod() not available on this system")

    @classmethod
    def lchmod(cls, *args, **kwargs):
        raise NotImplementedError("lchmod() not available on this system")

    @classmethod
    def mkdir(cls, *args, **kwargs):
        raise NotImplementedError("mkdir() not available on this system")

    @classmethod
    def unlink(cls, *args, **kwargs):
        raise NotImplementedError("unlink() not available on this system")

    @classmethod
    def link_to(cls, *args, **kwargs):
        raise NotImplementedError("link_to() not available on this system")

    @classmethod
    def rmdir(cls, *args, **kwargs):
        raise NotImplementedError("rmdir() not available on this system")

    @classmethod
    def rename(cls, *args, **kwargs):
        raise NotImplementedError("rename() not available on this system")

    @classmethod
    def replace(cls, *args, **kwargs):
        raise NotImplementedError("replace() not available on this system")

    @classmethod
    def symlink(cls, *args, **kwargs):
        raise NotImplementedError("symlink() not available on this system")

    @classmethod
    def readlink(cls, *args, **kwargs):
        raise NotImplementedError("readlink() is unsupported on this system")

    @classmethod
    def owner(cls, *args, **kwargs):
        raise NotImplementedError("owner() is unsupported on this system")

    @classmethod
    def group(cls, *args, **kwargs):
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

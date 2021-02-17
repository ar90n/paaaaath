import os
import pathlib
from pathlib import PurePosixPath, PureWindowsPath


class Path(pathlib.Path):
    def __new__(cls, *args, **kwargs):
        cls = cls.get_path_cls(*args)
        self = cls._from_parts(args, init=False)
        if not self._flavour.is_supported:
            raise NotImplementedError(
                "cannot instantiate %r on your system" % (cls.__name__,)
            )
        self._init()
        return self

    @classmethod
    def get_path_cls(cls, *args):
        if cls is not Path:
            return cls

        if 0 < len(args) and (
            args[0].startswith("http://") or args[0].startswith("https://")
        ):
            from .http import HttpPath

            return HttpPath

        return WindowsPath if os.name == "nt" else PosixPath


class PosixPath(Path, PurePosixPath):
    __slots__ = ()


class WindowsPath(Path, PureWindowsPath):
    __slots__ = ()

    def is_mount(self):
        raise NotImplementedError("Path.is_mount() is unsupported on this system")

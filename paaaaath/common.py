import os
import pathlib


class PurePath(pathlib.PurePath):
    def __new__(cls, *args):
        cls = cls.get_concrete_cls(*args)
        return cls._from_parts(args)

    @classmethod
    def get_concrete_cls(cls, *args):
        if cls is not PurePath:
            return cls

        if 0 < len(args) and (
            args[0].startswith("http://") or args[0].startswith("https://")
        ):
            from .http import PureHttpPath

            return PureHttpPath

        if 0 < len(args) and args[0].startswith("s3://"):
            from .s3 import PureS3Path

            return PureS3Path

        if os.name == "nt":
            from .windows import PureWindowsPath

            return PureWindowsPath

        from .posix import PurePosixPath

        return PurePosixPath


class Path(PurePath, pathlib.Path):
    def __new__(cls, *args, **kwargs):
        cls = cls.get_concrete_cls(*args)
        self = cls._from_parts(args, init=False)
        if not self._flavour.is_supported:
            raise NotImplementedError(
                "cannot instantiate %r on your system" % (cls.__name__,)
            )
        self._init()
        return self

    @classmethod
    def get_concrete_cls(cls, *args):
        if cls is not Path:
            return cls

        if 0 < len(args) and (
            args[0].startswith("http://") or args[0].startswith("https://")
        ):
            from .http import HttpPath

            return HttpPath

        if 0 < len(args) and args[0].startswith("s3://"):
            from .s3 import S3Path

            return S3Path

        if os.name == "nt":
            from .windows import WindowsPath

            return WindowsPath

        from .posix import PosixPath

        return PosixPath

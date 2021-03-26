import pathlib

from paaaaath.common import Path, PurePath


class PurePosixPath(PurePath, pathlib.PurePosixPath):
    __slots__ = ()


class PosixPath(Path, PurePosixPath, pathlib.PosixPath):
    __slots__ = ()

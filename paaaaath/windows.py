import pathlib

from paaaaath.common import Path, PurePath


class PureWindowsPath(PurePath, pathlib.PureWindowsPath):
    __slots__ = ()


class WindowsPath(Path, PureWindowsPath, pathlib.WindowsPath):
    __slots__ = ()

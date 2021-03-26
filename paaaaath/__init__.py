from .common import Path, PurePath
from .gcs import GCSPath, PureGCSPath
from .http import HttpPath, PureHttpPath
from .posix import PosixPath, PurePosixPath
from .s3 import PureS3Path, S3Path
from .uri import PureUriPath
from .windows import PureWindowsPath, WindowsPath

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # type: ignore

__version__ = version(__name__)

__all__ = [
    "Path",
    "PurePath",
    "GCSPath",
    "PureGCSPath",
    "HttpPath",
    "PureHttpPath",
    "PosixPath",
    "PurePosixPath",
    "PureS3Path",
    "S3Path",
    "PureUriPath",
    "PureWindowsPath",
    "WindowsPath",
]

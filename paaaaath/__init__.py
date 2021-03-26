from .common import Path, PurePath
from .http import HttpPath, PureHttpPath
from .posix import PosixPath, PurePosixPath
from .s3 import PureS3Path, S3Path
from .gcs import PureGCSPath, GCSPath
from .uri import PureUriPath
from .windows import PureWindowsPath, WindowsPath

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # type: ignore

__version__ = version(__name__)

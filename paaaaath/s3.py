import pathlib

import boto3
from botocore.exceptions import ClientError
from smart_open import smart_open_lib

from .common import Path, PurePath
from .uri import _UriFlavour


def _exists(client, bucket, key) -> bool:
    if key == "" or key == "/":
        return True

    try:
        client.head(bucket, key)
    except ClientError as e:
        return False
    return True


def _to_file_key(key) -> str:
    return key.rstrip("/")


def _to_dir_key(key) -> str:
    return key if key.endswith("/") else f"{key}/"


def _get_file_and_dir_exists(client, bucket, key):
    has_file = _exists(client, bucket, _to_file_key(key))
    has_dir = _exists(client, bucket, _to_dir_key(key))
    return has_file, has_dir


class S3Client:
    def __init__(self) -> None:
        self._client = boto3.client("s3")

    def get(self, bucket: str, key: str):
        return self._client.get_object(Bucket=bucket, Key=key)

    def put(self, bucket: str, key: str):
        self._client.put_object(Bucket=bucket, Key=key)

    def head(self, bucket: str, key: str):
        return self._client.head_object(Bucket=bucket, Key=key)

    def copy(self, source: str, bucket: str, key: str):
        self._client.copy_object(Bucket=bucket, CopySource=source, Key=key)

    def delete(self, bucket: str, key: str):
        self._client.delete_object(Bucket=bucket, Key=key)


class _S3Flavour(_UriFlavour):
    def splitroot(self, part, sep=None):
        sep = self.sep if sep is None else sep
        drv, root, part = super().splitroot(part, sep)

        if drv != "" and not drv.startswith("s3"):
            raise ValueError(f"http and https are only supported. but {drv} was given.")

        return drv, root, part


_s3_flavour = _S3Flavour()


class PureS3Path(PurePath):
    _flavour = _s3_flavour
    __slots__ = ()

    @property
    def bucket(self):
        if self.anchor == "":
            return ""
        return self.anchor[5:-1]

    @property
    def key(self):
        return self._flavour.sep.join(self.parts[1:])


class _S3Accessor(pathlib._Accessor):
    _client = S3Client()  # low-level client is thread safe

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

    def listdir(self, path: PureS3Path):
        def _get_child(content, base):
            return content["Key"].lstrip(base).lstrip("/").split("/")[0]

        contents = []
        continuation_token = ""
        while True:
            cur = self._client._client.list_objects_v2(
                Bucket=path.bucket,
                Prefix=path.key,
                ContinuationToken=continuation_token,
            )
            contents.extend([_get_child(c, cur["Prefix"]) for c in cur["Contents"]])
            if not cur["IsTruncated"]:
                break
            continuation_token = cur["NextContinuationToken"]
        return [c for c in contents if c != ""]

    @staticmethod
    def scandir(*args, **kwargs):
        raise NotImplementedError("scandir() not available on this system")

    @staticmethod
    def chmod(*args, **kwargs):
        raise NotImplementedError("chmod() not available on this system")

    @staticmethod
    def lchmod(*args, **kwargs):
        raise NotImplementedError("lchmod() not available on this system")

    def mkdir(self, path: PureS3Path, mode: int):
        if not _exists(self._client, path.bucket, _to_dir_key(path.parent.key)):
            raise FileNotFoundError

        key = _to_dir_key(path.key)
        if _exists(self._client, path.bucket, key):
            raise OSError
        self._client.put(path.bucket, key)

    def unlink(self, path):
        has_file, has_dir = _get_file_and_dir_exists(
            self._client, path.bucket, path.key
        )

        if has_file:
            self._client.delete(path.bucket, _to_file_key(path.key))
            return
        if has_dir:
            raise PermissionError
        raise FileNotFoundError

    @staticmethod
    def link_to(*args, **kwargs):
        raise NotImplementedError("link_to() not available on this system")

    def rmdir(self, path):
        has_file, has_dir = _get_file_and_dir_exists(
            self._client, path.bucket, path.key
        )
        if has_file:
            raise NotADirectoryError

        delete_objects = []
        continuation_token = ""
        while True:
            cur = self._client._client.list_objects_v2(
                Bucket=path.bucket,
                Prefix=_to_dir_key(path.key),
                ContinuationToken=continuation_token,
            )
            if "Contents" not in cur:
                break
            delete_objects.extend([{"Key": c["Key"]} for c in cur["Contents"]])
            if not cur["IsTruncated"]:
                break
            continuation_token = cur["NextContinuationToken"]

        if 0 < len(delete_objects):
            self._client._client.delete_objects(
                Bucket=path.bucket, Delete={"Objects": delete_objects}
            )
            return

        raise FileNotFoundError

    def rename(self, path, target: "S3Path"):
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

    def touch(self, mode=0x666, exist_ok=True):
        if exist_ok:
            try:
                source = f"{self.bucket}/{self.key}"
                self._accessor._client.copy(source, self.bucket, self.key)
            except ClientError:
                pass
            else:
                return
        self._accessor._client.put(self.bucket, self.key)

    def is_dir(self):
        return _exists(self._accessor._client, self.bucket, _to_dir_key(self.key))

    def is_file(self):
        return _exists(self._accessor._client, self.bucket, _to_file_key(self.key))

    def is_block_device(self):
        return False

    def is_char_device(self):
        return False

    def is_fifo(self):
        return False

    def is_socket(self):
        return False

    def exists(self):
        return self.is_dir() or self.is_file()

    def glob(self, pattern):
        raise NotImplementedError("Path.glob() is unsupported on this system")

    def rglob(self, pattern):
        raise NotImplementedError("Path.rglob() is unsupported on this system")

    def absolute(self):
        raise NotImplementedError("Path.absolute() is unsupported on this system")
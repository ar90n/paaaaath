import boto3
from botocore.exceptions import ClientError
from smart_open import smart_open_lib

from .common import PurePath, _SkeletonPath
from .uri import _UriFlavour


def _to_file_key(key) -> str:
    return key.rstrip("/")


def _to_dir_key(key) -> str:
    return key if key.endswith("/") else f"{key}/"


class _S3Flavour(_UriFlavour):
    def splitroot(self, part, sep=None):
        sep = self.sep if sep is None else sep
        drv, root, part = super().splitroot(part, sep)

        if drv != "" and not drv.startswith("s3://"):
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


class S3Path(_SkeletonPath, PureS3Path):
    __slots__ = ()
    _client = boto3.client("s3")  # low-level client is thread safe

    def open(self, *args, **kwargs):
        return smart_open_lib.open(str(self), *args, **kwargs)

    def touch(self, mode=0x666, exist_ok=True):
        if not self._exists(_to_dir_key(self.parent.key)):
            raise FileNotFoundError

        if exist_ok:
            try:
                source = f"{self.bucket}/{self.key}"
                self._client.copy_object(
                    CopySource=source, Bucket=self.bucket, Key=self.key
                )
            except ClientError:
                pass
            else:
                return
        if not exist_ok and self.exists():
            raise FileExistsError
        self._client.put_object(Bucket=self.bucket, Key=self.key)

    def exists(self):
        file_key = _to_file_key(self.key)
        dir_key = _to_dir_key(self.key)
        return self._exists(file_key) or self._exists(dir_key)

    def _mkdir(self, mode=0x777):
        if not self._exists(_to_dir_key(self.parent.key)):
            raise FileNotFoundError

        if self.exists():
            raise OSError
        self._client.put_object(Bucket=self.bucket, Key=_to_dir_key(self.key))

    def iterdir(self):
        def _get_child(content, base):
            return content["Key"].lstrip(base).lstrip("/").split("/")[0]

        continuation_token = ""
        while True:
            cur = self._client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.key,
                ContinuationToken=continuation_token,
            )
            names = (_get_child(c, cur["Prefix"]) for c in cur.get("Contents", []))
            for name in names:
                if name in {".", "..", ""}:
                    continue
                yield S3Path(f"{self.anchor}{self.key}/{name}")
            if not cur["IsTruncated"]:
                break
            continuation_token = cur["NextContinuationToken"]

    def is_dir(self):
        try:
            dir_key = _to_dir_key(self.key)
            res = self._client.head_object(Bucket=self.bucket, Key=dir_key)
            return res["ContentLength"] == 0
        except ClientError:
            return False

    def _exists(self, key) -> bool:
        if key == "" or key == "/":
            return True

        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
        except ClientError as e:
            return False
        return True

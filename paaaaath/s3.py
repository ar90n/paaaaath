import boto3
from botocore.exceptions import ClientError
from smart_open import smart_open_lib

from .blob import to_file_key, to_dir_key, PureBlobPath, _SkeletonBlobPath
from .uri import _UriFlavour


class _S3Flavour(_UriFlavour):
    schemes = ["s3"]


_s3_flavour = _S3Flavour()


class PureS3Path(PureBlobPath):
    _flavour = _s3_flavour
    __slots__ = ()


class S3Path(_SkeletonBlobPath, PureS3Path):
    __slots__ = ()

    def open(self, *args, **kwargs):
        return smart_open_lib.open(str(self), *args, **kwargs)

    def touch(self, mode=0x666, exist_ok=True):
        if not self._exists(to_dir_key(self.parent.key)):
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
        file_key = to_file_key(self.key)
        dir_key = to_dir_key(self.key)
        return self._exists(file_key) or self._exists(dir_key)

    def _mkdir(self, mode=0x777):
        if not self._exists(to_dir_key(self.parent.key)):
            raise FileNotFoundError

        if self.exists():
            raise OSError
        self._client.put_object(Bucket=self.bucket, Key=to_dir_key(self.key))

    def iterdir(self):
        def _get_child(content, base):
            return content["Key"].lstrip(base).lstrip("/").split("/")[0]

        continuationtoken = ""
        while True:
            cur = self._client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.key,
                ContinuationToken=continuationtoken,
            )
            names = (_get_child(c, cur["Prefix"]) for c in cur.get("Contents", []))
            for name in names:
                if name in {".", "..", ""}:
                    continue
                yield S3Path(f"{self.anchor}{self.key}/{name}")
            if not cur["IsTruncated"]:
                break
            continuationtoken = cur["NextContinuationToken"]

    def is_dir(self):
        try:
            dir_key = to_dir_key(self.key)
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

    @staticmethod
    def _create_client():
        return boto3.client("s3")  # low-level client is thread safe

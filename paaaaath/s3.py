import itertools

from smart_open import smart_open_lib

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    MISSING_DEPS = True
else:
    MISSING_DEPS = False

from paaaaath.blob import PureBlobPath, _SkeletonBlobPath, to_dir_key, to_file_key
from paaaaath.common import Path, PurePath
from paaaaath.uri import _UriFlavour


class _S3Flavour(_UriFlavour):
    schemes = ["s3"]


_s3_flavour = _S3Flavour()


@PurePath.register()
class PureS3Path(PureBlobPath):
    _flavour = _s3_flavour
    __slots__ = ()


@Path.register(MISSING_DEPS)
class S3Path(_SkeletonBlobPath, PureS3Path):
    __slots__ = ()

    def open(self, *args, **kwargs):
        kwargs = {
            **kwargs,
            "transport_params": {
                "resource_kwargs": {
                    "endpoint_url": self._client._endpoint.host,
                }
            },
        }
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
        key = to_dir_key(self.key) if self.key != "" else self.key
        cur = self._client.list_objects_v2(
            Bucket=self.bucket, Prefix=key, Delimiter="/"
        )
        while True:
            file_names = (c["Key"] for c in cur.get("Contents", []))
            dir_names = (c["Prefix"] for c in cur.get("CommonPrefixes", []))
            for name in itertools.chain(dir_names, file_names):
                if name in {".", "..", ""}:
                    continue
                yield S3Path(f"{self.anchor}/{name}")
            if not cur["IsTruncated"]:
                break
            cur = self._client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=key,
                Delimiter="/",
                ContinuationToken=cur["NextContinuationToken"],
            )

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

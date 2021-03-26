from smart_open import smart_open_lib
from smart_open.constants import WRITE_BINARY

try:
    from google.api_core.exceptions import NotFound
    from google.cloud import storage
    from smart_open import gcs
except ImportError:
    MISSING_DEPS = True
else:
    MISSING_DEPS = False

from paaaaath.blob import PureBlobPath, _SkeletonBlobPath, to_dir_key, to_file_key
from paaaaath.common import Path, PurePath
from paaaaath.uri import _UriFlavour


class _GCSFlavour(_UriFlavour):
    schemes = ["gs"]


_gcs_flavour = _GCSFlavour()


@PurePath.register()
class PureGCSPath(PureBlobPath):
    __slots__ = ()
    _flavour = _gcs_flavour


@Path.register(MISSING_DEPS)
class GCSPath(_SkeletonBlobPath, PureGCSPath):
    __slots__ = ()

    def open(self, *args, **kwargs):
        kwargs = {**kwargs, "transport_params": {"client": self._client}}
        return smart_open_lib.open(str(self), *args, **kwargs)

    def touch(self, mode=0x666, exist_ok=True):
        if not self._exists(to_dir_key(self.parent.key)):
            raise FileNotFoundError

        if exist_ok:
            try:
                bucket = self._client.get_bucket(self.bucket)
                bucket.copy_blob(bucket.get_blob(self.key), bucket, self.key)
            except NotFound:
                pass
            else:
                return
        if not exist_ok and self.exists():
            raise FileExistsError
        gcs.open(self.bucket, self.key, WRITE_BINARY, client=self._client).close()

    def exists(self):
        file_key = to_file_key(self.key)
        dir_key = to_dir_key(self.key)
        return self._exists(file_key) or self._exists(dir_key)

    def _mkdir(self, mode=0x777):
        if not self._exists(to_dir_key(self.parent.key)):
            raise FileNotFoundError

        if self.exists():
            raise OSError
        gcs.open(
            self.bucket, to_dir_key(self.key), WRITE_BINARY, client=self._client
        ).close()

    def iterdir(self):
        prefix = to_dir_key(self.key) if self.key != "" else self.key
        blobs = self._client.list_blobs(self.bucket, prefix=prefix, delimiter="/")
        for blob in blobs:
            if blob.name in {".", "..", prefix}:
                continue
            yield GCSPath(f"{self.anchor}/{blob.name}")
        for blob_prefix in blobs.prefixes:
            yield GCSPath(f"{self.anchor}/{blob_prefix}")

    def is_dir(self):
        dir_key = to_dir_key(self.key)
        blob = self._client.get_bucket(self.bucket).get_blob(dir_key)
        if blob is None:
            return False
        return blob.size == 0

    def _exists(self, key) -> bool:
        if key == "" or key == "/":
            return True

        return self._client.get_bucket(self.bucket).get_blob(key) is not None

    @classmethod
    def _create_client(cls):
        return storage.Client()

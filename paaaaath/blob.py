from paaaaath.common import PurePath, _SkeletonPath


def to_file_key(key: str) -> str:
    return key.rstrip("/")


def to_dir_key(key: str) -> str:
    return key if key.endswith("/") else f"{key}/"


def _get_scheme(anchor: str) -> str:
    if ":" not in anchor:
        return ""

    end = anchor.index(":") + 3
    return anchor[:end]


class PureBlobPath(PurePath):
    @property
    def bucket(self):
        if self.anchor == "":
            return ""

        beg = len(_get_scheme(self.anchor))
        return self.anchor[beg:-1]

    @property
    def key(self):
        return self._flavour.sep.join(self.parts[1:])


class _SkeletonBlobPath(_SkeletonPath):
    __client = None

    def _create_client(self):
        raise NotImplementedError("_create_client() must be implemented.")

    @property
    def _client(self):
        if self.__client is None:
            self.__client = self._create_client()
        return self.__client

    @classmethod
    def register_client(cls, client):
        cls.__client = client

from .common import PurePath


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

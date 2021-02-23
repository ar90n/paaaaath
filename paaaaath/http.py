from smart_open import smart_open_lib

from .common import PurePath, _SkeletonPath
from .uri import _UriFlavour


class _HttpFlavour(_UriFlavour):
    def splitroot(self, part, sep=None):
        sep = self.sep if sep is None else sep
        drv, root, part = super().splitroot(part, sep)

        if not any((drv == "" or drv.startswith(p) for p in ["http", "https"])):
            raise ValueError(f"http and https are only supported. but {drv} was given.")

        return drv, root, part


_http_flavour = _HttpFlavour()


class PureHttpPath(PurePath):
    _flavour = _http_flavour
    __slots__ = ()


class HttpPath(_SkeletonPath, PureHttpPath):
    __slots__ = ()

    def open(self, *args, **kwargs):
        return smart_open_lib.open(str(self), *args, **kwargs)

    def exists(self):
        from requests.exceptions import HTTPError

        try:
            self.open()
        except HTTPError:
            return False
        return True

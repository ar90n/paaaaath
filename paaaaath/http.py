from smart_open import smart_open_lib
from requests.exceptions import HTTPError

from .common import PurePath, _SkeletonPath
from .uri import _UriFlavour


class _HttpFlavour(_UriFlavour):
    schemes = ["http", "https"]


_http_flavour = _HttpFlavour()


class PureHttpPath(PurePath):
    _flavour = _http_flavour
    __slots__ = ()


class HttpPath(_SkeletonPath, PureHttpPath):
    __slots__ = ()

    def open(self, *args, **kwargs):
        return smart_open_lib.open(str(self), *args, **kwargs)

    def exists(self):
        try:
            self.open()
        except HTTPError:
            return False
        return True

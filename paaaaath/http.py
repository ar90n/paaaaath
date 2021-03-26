from smart_open import smart_open_lib

try:
    from requests.exceptions import HTTPError
except ImportError:
    MISSING_DEPS = True
else:
    MISSING_DEPS = False

from paaaaath.common import Path, PurePath, _SkeletonPath
from paaaaath.uri import _UriFlavour


class _HttpFlavour(_UriFlavour):
    schemes = ["http", "https"]


_http_flavour = _HttpFlavour()


@PurePath.register()
class PureHttpPath(PurePath):
    _flavour = _http_flavour
    __slots__ = ()


@Path.register(MISSING_DEPS)
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

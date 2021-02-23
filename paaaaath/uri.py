import fnmatch
import pathlib
import posixpath
import re
from os import fsencode
from urllib.parse import quote_from_bytes, urlparse

from .common import Path, PurePath


class _UriFlavour(pathlib._Flavour):
    sep = "/"
    altsep = ""
    has_drv = True
    pathmod = type("fakepath", (), {"normpath": lambda _, x: x})()

    is_supported = True

    def splitroot(self, part, sep=sep):
        url = urlparse(part)
        scheme = url.scheme
        netloc = url.netloc
        path = url.path

        if scheme == "" and netloc != "":
            path = f"{sep}{netloc}{sep}{path}".rstrip(sep)
            netloc = ""

        drv = f"{scheme}://{netloc}" if scheme != "" else ""
        part = path.lstrip("/")
        root = sep if drv != "" or path != part else ""
        return drv, root, part

    def casefold(self, s):
        return s

    def casefold_parts(self, parts):
        return parts

    def compile_pattern(self, pattern):
        return re.compile(fnmatch.translate(pattern)).fullmatch

    def resolve(self, path, strict=False):
        norm_path = posixpath.normpath(self.join(path.parts[1:]))
        return f"{path.drive}{path.root}{norm_path}"

    def is_reserved(self, parts):
        return False

    def make_uri(self, path):
        bpath = bytes(fsencode(self.join(path.parts[1:])))
        return f"{path.drive}{path.root}{quote_from_bytes(bpath)}"

    def gethomedir(self, username):
        raise NotImplementedError("gethomedir() not available on this system")


_uri_flavour = _UriFlavour()


class PureUriPath(PurePath):
    _flavour = _uri_flavour
    __slots__ = ()

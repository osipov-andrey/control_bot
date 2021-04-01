import os
import gzip
import shutil

from logging import handlers


__all__ = ["gzip_rotating_handler"]


def namer(name):
    return name + ".gz"


def rotator(source, dest):
    with open(source, "rb") as sf:
        with gzip.open(dest, "wb", compresslevel=9) as df:
            shutil.copyfileobj(sf, df)

    os.remove(source)


def gzip_rotating_handler(*args, **kwargs):
    handler = handlers.TimedRotatingFileHandler(*args, **kwargs)
    handler.namer = namer
    handler.rotator = rotator

    return handler

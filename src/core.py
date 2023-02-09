from __future__ import annotations

import functools
import typing

if typing.TYPE_CHECKING:
    from src.typings import EventHandler


def rename(name: str):
    def wrapper(handler: EventHandler):
        @functools.wraps(handler)
        async def wrapped(*args, **kwargs):
            return await handler(*args, **kwargs)

        wrapped.__name__ = name

        return wrapped

    return wrapper

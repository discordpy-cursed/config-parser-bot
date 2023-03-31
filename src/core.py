import functools

from discord.utils import MISSING

from src.typings import EventHandler


def listen(name: str = MISSING):
    def wrapper(handler: EventHandler):
        @functools.wraps(handler)
        async def wrapped(*args, **kwargs):
            return await handler(*args, **kwargs)

        # https://github.com/Rapptz/discord.py/blob/bb7668f8a58ba4b8161edeb77f8936ff807d6537/discord/ext/commands/bot.py#L602-L628
        wrapped.__name__ = wrapped.__name__ if name is MISSING else name

        return wrapped

    return wrapper

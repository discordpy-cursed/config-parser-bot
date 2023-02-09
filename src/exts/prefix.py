from __future__ import annotations

import os
import typing

if typing.TYPE_CHECKING:
    from src.bot import Bot

STATIC_FALLBACK_PREFIX = "?"


async def command_prefix(*_) -> str | tuple[str]:
    return os.environ.get("PREFIX", STATIC_FALLBACK_PREFIX)


async def setup(bot: Bot):
    bot.command_prefix = command_prefix


async def teardown(bot: Bot):
    bot.command_prefix = STATIC_FALLBACK_PREFIX

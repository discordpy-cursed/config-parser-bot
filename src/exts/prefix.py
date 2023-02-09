from __future__ import annotations

import os
import typing
from dotenv import load_dotenv

from src.constants import STATIC_FALLBACK_PREFIX

if typing.TYPE_CHECKING:
    from src.bot import Bot


async def command_prefix(*_) -> str:
    return os.environ.get("PREFIX", STATIC_FALLBACK_PREFIX)


async def setup(bot: Bot):
    bot.command_prefix = command_prefix

    load_dotenv(override=True)


async def teardown(bot: Bot):
    bot.command_prefix = STATIC_FALLBACK_PREFIX

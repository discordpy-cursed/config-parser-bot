from __future__ import annotations

import os
import typing

import discord

if typing.TYPE_CHECKING:
    from src.bot import Bot

STATIC_FALLBACK_PREFIX = "?"


async def command_prefix(bot: Bot, message: discord.Message) -> str | tuple[str]:
    return os.environ.get("PREFIX", STATIC_FALLBACK_PREFIX)


async def setup(bot: Bot):
    bot.command_prefix = command_prefix


async def teardown(bot: Bot):
    bot.command_prefix = STATIC_FALLBACK_PREFIX

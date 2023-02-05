from __future__ import annotations

import typing

import discord
from discord.ext import commands

if typing.TYPE_CHECKING:
    from src.bot import Bot


async def on_message(self: Bot, message: discord.Message):
    await self.process_commands(message)


# TODO: replace bot type with custom bot type via type_checking
# TODO: refactor so that `overridden_on_message` is not externally depended on
async def setup(bot: Bot):
    bot.overridden_on_message = on_message


async def teardown(bot: Bot):
    disable_overridden_on_message = None

    bot.overridden_on_message = disable_overridden_on_message

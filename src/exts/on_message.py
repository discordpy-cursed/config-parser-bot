from __future__ import annotations

import typing

import discord
from discord.ext import commands

if typing.TYPE_CHECKING:
    from src.bot import Bot


async def on_message(bot: Bot, message: discord.Message):
    await bot.process_commands(message)


async def setup(bot: Bot):
    bot.on_message = on_message


async def teardown(bot: Bot):
    disable_overridden_on_message = None

    bot.on_message = disable_overridden_on_message

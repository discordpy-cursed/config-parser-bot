from __future__ import annotations

import typing

import discord

if typing.TYPE_CHECKING:
    from src.bot import Bot


async def on_message(bot: Bot, message: discord.Message):
    await bot.process_commands(message)


# TODO: abstract setups and teardowns when missing
# TODO: prefer decorators over explicit calls to add_x methods
async def setup(bot: Bot):
    bot.add_event(on_message)

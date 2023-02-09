from __future__ import annotations

import typing

import discord

if typing.TYPE_CHECKING:
    from src import Bot


async def balls(bot: Bot, reaction: discord.Emoji | discord.PartialEmoji, user: discord.User):
    print("[Added Reaction]", f"{user} (Admin: {await bot.is_owner(user)})", reaction, sep="\n", end="\n\n")


async def setup(bot: Bot):
    bot.add_event("on_reaction_add", balls)

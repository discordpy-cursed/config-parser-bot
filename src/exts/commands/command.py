from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from src.bot import Bot

from discord.ext import commands


@commands.command()
async def command(ctx: commands.Context):
    await ctx.send(str(ctx.command))


async def setup(bot: Bot):
    bot.add_command(command)

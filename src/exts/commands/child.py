from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from src.bot import Bot

from discord.ext import commands


@commands.command()
async def child(ctx: commands.Context):
    await ctx.send(str(ctx.command))


async def setup(bot: Bot):
    bot.add_command(child)


# async def teardown(bot: Bot):
#     bot.remove_command(command.name)

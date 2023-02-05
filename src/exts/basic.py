from __future__ import annotations

import typing

from discord.ext import commands

if typing.TYPE_CHECKING:
    from src.bot import Bot


class Basic(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def command(self, ctx: commands.Context):
        await ctx.send(str(ctx.command))

    @commands.command()
    async def group(self, ctx: commands.Context):
        await ctx.send(str(ctx.command))

    @commands.command()
    async def child(self, ctx: commands.Context):
        await ctx.send(str(ctx.command))


async def setup(bot: Bot):
    await bot.add_cog(Basic(bot))

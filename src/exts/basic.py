import discord
from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, bot):
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Basic(bot))

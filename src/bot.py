"""
So I want to create a system that enables both team members to run their own commands with whatever prefix they choose,
the prefix aspect is already setup, though the problem here is actually being able to differentiate between the 2 users
initially. There's a way to grab the ID of the application owner so maybe looking there would be better to look into.
"""
import asyncio
import contextlib
import os
import pathlib
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

log = logging.getLogger('bot')


class TestingBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="?",
            intents=discord.Intents.all(),
        )

    async def load_extension(self, extension: str):
        try:
            await super().load_extension(extension)
            log.info(f'Loaded extension {extension!r}')
        except Exception as error:
            log.error(f'Failed to load extension {extension!r}', exc_info=error)

    async def unload_extension(self, extension: str):
        try:
            await super().unload_extension(extension)
            log.info(f'Unloaded extension {extension!r}')
        except Exception as error:
            log.error(f'Failed to unload extension {extension!r}', exc_info=error)

    async def setup_hook(self) -> None:
        for file in pathlib.Path('exts').glob('**/*.py'):
            *tree, _ = file.parts
            ext = f"{'.'.join(tree)}.{file.stem}"

            await self.load_extension(ext)


async def main(token: str):
    async with TestingBot() as bot:
        discord.utils.setup_logging()
        await bot.start(token)


if __name__ == '__main__':
    load_dotenv()

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main(os.environ['TOKEN']))

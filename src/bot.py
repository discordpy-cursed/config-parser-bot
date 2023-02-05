import asyncio
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

    async def setup_hook(self) -> None:
        for file in pathlib.Path('exts').glob('**/*.py'):
            *tree, _ = file.parts
            ext = f"{'.'.join(tree)}.{file.stem}"
            try:
                await self.load_extension(ext)
                log.info(f'Loaded extension {ext!r}')
            except Exception as e:
                log.error(f'Failed to load extension {ext!r}', exc_info=e)


async def start(token: str):
    async with TestingBot() as bot:
        discord.utils.setup_logging()
        await bot.start(token)

if __name__ == '__main__':
    load_dotenv()
    asyncio.run(start(os.environ['TOKEN']))

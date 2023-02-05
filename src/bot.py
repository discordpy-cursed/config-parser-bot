from typing import Callable, Optional, Coroutine, Any
import tomllib
import asyncio
import os
import pathlib
import logging
from pprint import pformat

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import Config

log = logging.getLogger('bot')


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="?",
            intents=discord.Intents.all(),
        )

        self.overridden_on_message: Callable[[Bot, discord.Message], Coroutine[Any, Any, None]] | None = None

        with open('config.toml', 'rb') as fp:
            config_payload = tomllib.load(fp)
            self.config = Config(**config_payload)

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

    async def setup_hook(self):
        await self.load_extension("jishaku")

        for file in pathlib.Path('src/exts').glob('**/*.py'):
            *tree, _ = file.parts
            ext = f"{'.'.join(tree)}.{file.stem}"
            await self.load_extension(ext)
            log.info(f'Loaded extension {ext!r}')

    async def on_message(self, message: discord.Message):
        if self.overridden_on_message:
            bot = self


async def start(token: str):
    async with Bot() as bot:
        discord.utils.setup_logging()
        await bot.setup_hook()


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(start(os.environ['TOKEN']))

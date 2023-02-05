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


class TestingBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="?",
            intents=discord.Intents.all(),
        )
        self._config: Optional[Config] = None

    @property
    def config(self) -> Config:
        if self._config:
            return self.config
        raise RuntimeError('Bot is not initialized yet')

    @config.setter
    def config(self, config: Config):
        self._config = config

    async def setup_hook(self) -> None:
        for file in pathlib.Path('exts').glob('**/*.py'):
            *tree, _ = file.parts
            ext = f"{'.'.join(tree)}.{file.stem}"
            try:
                await self.load_extension(ext)
                log.info(f'Loaded extension {ext!r}')
            except Exception as e:
                log.error(f'Failed to load extension {ext!r}', exc_info=e)

        with open('config.toml', 'rb') as fp:
            cfgpayload = tomllib.load(fp)
            self.config = Config(**cfgpayload)


async def start(token: str):
    async with TestingBot() as bot:
        discord.utils.setup_logging()
        await bot.setup_hook()

if __name__ == '__main__':
    load_dotenv()
    asyncio.run(start(os.environ['TOKEN']))

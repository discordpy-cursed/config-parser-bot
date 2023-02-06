from __future__ import annotations

import contextlib
import logging
import os
import pathlib
import tomllib
import typing

import discord
from discord.ext import commands

from src.config import Config

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Coroutine

log = logging.getLogger('bot')


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=os.environ["PREFIX"],
            intents=discord.Intents.all(),
        )

        self.overridden_on_message: Callable[[Bot, discord.Message], Coroutine[Any, Any, None]] | None = None

        with open('config.toml', 'rb') as fp:
            config_payload = tomllib.load(fp)
            self.config = config_payload  # Config(**config_payload)

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
        """
        I want to make it so if Jishaku exists, I only import it based on the config file.

        The first part is easy as shown below, the second part relies on the config actually being initialised in the first place.
        Wondering if there's a need for an entry point in code.
        """
        with contextlib.suppress(commands.ExtensionNotFound):
            # TODO: replace with config value
            if True:
                await self.load_extension("jishaku")

        for file in pathlib.Path('src/exts').glob('**/*.py'):
            *tree, _ = file.parts
            ext = f"{'.'.join(tree)}.{file.stem}"

            await self.load_extension(ext)

    async def on_message(self, message: discord.Message):
        if self.overridden_on_message:
            bot = self

            try:
                return await self.overridden_on_message(bot, message)
            except Exception as error:
                log.error('Failed to process overridden on_message', exc_info=error)

        await self.process_commands(message)

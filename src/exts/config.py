from __future__ import annotations

import tomllib
import typing

from src import Config

if typing.TYPE_CHECKING:
    from src.bot import Bot


async def setup(bot: Bot):
    with open('config.toml', 'rb') as fp:
        bot.config = Config(**tomllib.load(fp))

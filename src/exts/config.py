from __future__ import annotations

import tomllib
import typing

from src.config import Config

if typing.TYPE_CHECKING:
    from src.bot import Bot


def setup(bot: Bot):
    with open('config.toml', 'rb') as fp:
        bot.config = Config(**tomllib.load(fp))

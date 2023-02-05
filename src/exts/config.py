import tomllib

from config import Config
from bot import Bot


def setup(bot: Bot):
    with open('src/config.toml', 'rb') as fp:
        bot.config = Config(**tomllib.load(fp))

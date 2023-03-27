import asyncio
import contextlib
import os

import discord
from dotenv import load_dotenv
from watchdog.observers import Observer

from src import config
from src.bot import Bot
from src.exts.hmr import HotModuleReloader


async def main(token: str):
    hot_module_reloader = HotModuleReloader()

    async with Bot() as bot:
        discord.utils.setup_logging()

        hot_module_reloader.start(bot)
        await bot.start(token)

    hot_module_reloader.stop()


if __name__ == '__main__':
    load_dotenv()
    config.assert_prerequisites()

    with contextlib.suppress(KeyboardInterrupt, asyncio.CancelledError):
        asyncio.run(main(os.environ['TOKEN']))

import asyncio
import contextlib
import os

import discord
from dotenv import load_dotenv

from src import config, hmr
from src.bot import Bot


async def main():
    token = os.environ['TOKEN']

    async with Bot() as bot:
        await asyncio.gather(bot.start(token), hmr.start(bot))


if __name__ == '__main__':
    load_dotenv()
    config.assert_prerequisites()
    discord.utils.setup_logging()

    with contextlib.suppress(KeyboardInterrupt, RuntimeError, asyncio.CancelledError):
        asyncio.run(main())

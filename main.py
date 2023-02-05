import asyncio
import contextlib
import os

import discord
from dotenv import load_dotenv

from src.bot import Bot


async def main(token: str):
    async with Bot() as bot:
        discord.utils.setup_logging()
        await bot.start(token)


if __name__ == '__main__':
    load_dotenv()

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main(os.environ['TOKEN']))

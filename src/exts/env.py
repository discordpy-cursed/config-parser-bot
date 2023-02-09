from __future__ import annotations

import typing

from dotenv import load_dotenv

if typing.TYPE_CHECKING:
    from src.bot import Bot


async def setup(_: Bot):
    load_dotenv()

from __future__ import annotations

import typing

from discord.ext import commands

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Coroutine

    EventHandler = Callable[[commands.Bot, *Any], Coroutine[Any, Any, Any]]

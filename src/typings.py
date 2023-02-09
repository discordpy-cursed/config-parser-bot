from __future__ import annotations

from typing import Any, Callable, Coroutine, TypeAlias

from src.bot import Bot

EventHandler: TypeAlias = Callable[[Bot, *Any], Coroutine[Any, Any, Any]]

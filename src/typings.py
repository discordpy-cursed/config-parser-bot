from __future__ import annotations

from typing import Any, Callable, Coroutine

from src.bot import Bot

EventHandler = Callable[[Bot, *Any], Coroutine[Any, Any, Any]]

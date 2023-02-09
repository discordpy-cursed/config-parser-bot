from __future__ import annotations

from typing import Any

from discord.ext import commands

from src.bot import Bot

CommandT = commands.Command[None, ..., Any]
GroupT = commands.Group[None, ..., Any]
HybridCommandT = commands.HybridCommand[Any, ..., Any]
HybridGroupT = commands.HybridGroup[Any, ..., Any]
Invokable = CommandT | GroupT
Context = commands.Context[Bot]

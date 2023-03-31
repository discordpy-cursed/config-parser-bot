from __future__ import annotations

import contextlib
import importlib
import os
import types
import typing
from importlib.machinery import ModuleSpec

import watchfiles
from discord.ext import commands

from src.errors import ModuleError, ModuleFailed

if typing.TYPE_CHECKING:
    import importlib.util

    from src.bot import Bot

CWD = os.getcwd()


def path_to_mod(filepath: str) -> str:
    if filepath.startswith("/"):
        filepath = filepath[1:]
    elif filepath.startswith("./"):
        filepath = filepath[2:]

    return filepath.replace("/", ".").replace(".py", "")


async def process_change(bot: Bot, change_type: watchfiles.Change, filepath: str):
    if change_type is not watchfiles.Change.modified or not filepath.endswith(".py"):
        return

    resolved_filepath = os.path.abspath(filepath)
    accurate_relative_filepath = os.path.relpath(resolved_filepath, start=CWD)
    as_module_path = path_to_mod(accurate_relative_filepath)

    if as_module_path.startswith("src.exts"):
        with contextlib.suppress(commands.ExtensionError):
            return await bot.reload_extension(as_module_path)

    spec_found = importlib.util.find_spec(as_module_path)

    if not spec_found:
        return

    module_found: types.ModuleType = importlib.util.module_from_spec(spec_found)

    if not module_found:
        return

    try:
        bot.load_module(as_module_path, spec=spec_found, module=module_found)
    except ModuleFailed:
        return

    base_bot_class_found = getattr(module_found, "Bot", None)

    if not base_bot_class_found:
        try:
            return bot.reload_module(as_module_path)
        except ImportError:
            return None

    # this attribute stores the old class, so we swap the reference with the
    # updated class and attribute/method lookups dynamically sync by default
    bot.__class__ = base_bot_class_found


async def start(bot: Bot):
    async for changes in watchfiles.awatch("./"):
        for change_type, filepath in changes:
            await process_change(bot, change_type, filepath)

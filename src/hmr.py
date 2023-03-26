from __future__ import annotations

import asyncio
import contextlib
import importlib
import logging
import pathlib
import types
import typing
from importlib.machinery import ModuleSpec

from discord.ext import commands
from watchdog.events import FileModifiedEvent, FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

if typing.TYPE_CHECKING:
    from src.bot import Bot

log = logging.getLogger("HMR")


class FileEditEventHandler(FileSystemEventHandler):
    def __init__(self, bot: Bot, *, quiet: bool = False):
        self.bot = bot
        self.quiet = quiet

    def info(self, message: str):
        if self.quiet:
            return

        log.info(message)

    def error(self, message: str):
        if self.quiet:
            return

        log.error(message)

    def dispatch(self, event: FileSystemEvent):
        try:
            super().dispatch(event)
        except Exception as error:
            log.error(f'Watchdog {event.event_type!r} event failed:', exc_info=error)

    def to_module_path(self, filepath: str) -> str:
        return filepath.replace("./", "", 1).replace(".py", "", 1).replace("/", ".")

    # instead of reloading the file when modified which causes multiple events
    # and antential duplicate behavour, we reload when the system closes the
    # file instead as this only occurs after opening/modifying
    def on_closed(self, event: FileModifiedEvent):
        path = pathlib.Path(event.src_path)
        parents = [p.name for p in path.parents]
        is_python_artifact = "__pycache__" in parents

        if event.is_directory or is_python_artifact:
            return

        module_path = self.to_module_path(event.src_path)
        module_spec_found: ModuleSpec = importlib.util.find_spec(module_path)

        if not module_spec_found:
            return

        module: types.ModuleType = importlib.util.module_from_spec(module_spec_found)

        try:
            module_spec_found.loader.exec_module(module)
        except Exception as error:
            self.error(f'Failed to load module {module_path!r}', exc_info=error)

            raise error

        has_entry_point = getattr(module, "setup", False)

        if has_entry_point:
            self.info(f'Reloading extension {module_path!r}...')

            with contextlib.suppress(commands.CommandError):
                asyncio.run(self.bot.reload_extension(module_path))

            return self.info(f'Reloaded extension {module_path!r}')

        self.info(f'Reloading module {module_path!r}...')
        self.bot.reload_module(module_path, spec=module_spec_found, module=module)
        self.info(f'Reloaded module {module_path!r}')


class HotModuleReloader(Observer):
    def start(self, bot: Bot):
        hot_module_reloader = FileEditEventHandler(bot)

        self.schedule(hot_module_reloader, path="./src", recursive=True)
        super().start()

    def stop(self):
        super().stop()
        self.join()


def setup(bot: Bot):
    bot.hot_module_reloader = HotModuleReloader(bot)


def teardown(bot: Bot):
    bot.hot_module_reloader.stop()

    bot.hot_module_reloader = None

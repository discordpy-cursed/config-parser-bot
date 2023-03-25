from __future__ import annotations

import asyncio
import logging
import pathlib
import typing

from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent, FileSystemEventHandler

if typing.TYPE_CHECKING:
    from .bot import Bot

log = logging.getLogger("HMR")


class FileEditEventHandler(FileSystemEventHandler):
    def __init__(self, bot: Bot, *, quiet: bool = False):
        self.bot = bot
        self.quiet = quiet

    def to_module_path(self, filepath: str) -> str:
        return filepath.replace("./", "", 1).replace(".py", "", 1).replace("/", ".")

    # instead of reloading the file when modified, reload when the system closes
    # it, which only occurs after opening/modifying
    def on_closed(self, event: FileModifiedEvent):
        path = pathlib.Path(event.src_path)
        parents = [p.name for p in path.parents]
        is_python_artifact = "__pycache__" in parents

        if event.is_directory or is_python_artifact:
            return

        module_path = self.to_module_path(event.src_path)

        if not self.quiet:
            log.info(f"Reloading {module_path}...")

        asyncio.run(self.bot.reload_extension(module_path))


class HotModuleReloader(Observer):
    def start(self, bot: Bot):
        hot_module_reloader = FileEditEventHandler(bot)

        self.schedule(hot_module_reloader, path="./src", recursive=True)
        super().start()

    def stop(self):
        super().stop()
        self.join()

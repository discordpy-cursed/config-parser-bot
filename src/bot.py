from __future__ import annotations

import contextlib
import logging
import pathlib
import typing
from typing import overload

import discord
from discord.ext import commands

from src.commands import process_command
from src.config import Config
from src.exts.prefix import command_prefix

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Coroutine

    EventHandler = Callable[[commands.Bot, *Any], Coroutine[Any, Any, Any]]
    Listener = Callable[..., Coroutine[Any, Any, Any]]

log = logging.getLogger('bot')


# TODO: bot HMR
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=command_prefix,
            intents=discord.Intents.all(),
        )

        self.config: Config | None = None
        self.events: dict[str, set[EventHandler]] = {}

    @overload
    def add_event(self, callback: EventHandler):
        ...

    @overload
    def add_event(self, name: str, callback: EventHandler):
        ...

    def add_event(self, name_or_handler: str | EventHandler, callback: EventHandler | None = None):
        name: str = name_or_handler
        handler: EventHandler | None = callback

        if callback is None:
            handler = name_or_handler
            name = handler.__name__

        events = self.events.setdefault(name, set())

        events.add(handler)

    @overload
    def remove_event(self, name: str):
        ...

    @overload
    def remove_event(self, handler: EventHandler):
        ...

    # TODO: rewrite documentation
    def remove_event(self, name_or_handler: str | EventHandler):
        """
        When given a string, it is treated as being passed an event and all events associated with it are removed.
        When given an event handler/callback, it is sought for and removed.
        """
        if not isinstance(name_or_handler, str):
            for handlers in self.events.values():
                if name_or_handler not in handlers:
                    continue

                handlers.remove(name_or_handler)

            return

        name = name_or_handler if name_or_handler.startswith("on_") else f"on_{name_or_handler}"
        events_found = self.events.get(name, False)

        if not events_found:
            return

        del self.events[name]

    async def load_extension(self, extension: str):
        try:
            await super().load_extension(extension)
            log.info(f'Loaded extension {extension!r}')
        except Exception as error:
            log.error(f'Failed to load extension {extension!r}', exc_info=error)

    def handle_unloading_event_cleanup(self, extension: str):
        for handlers in self.events.values():
            from_extension = [handler for handler in handlers if handler.__module__ == extension]

            for callback in from_extension:
                handlers.remove(callback)

    async def reload_extension(self, name: str) -> None:
        return await super().reload_extension(name)

    async def unload_extension(self, extension: str):
        try:
            await super().unload_extension(extension)
            log.info(f'Unloaded extension {extension!r}')
        except Exception as error:
            log.error(f'Failed to unload extension {extension!r}', exc_info=error)

    async def _remove_module_references(self, name: str) -> None:
        await super()._remove_module_references(name)
        self.handle_unloading_event_cleanup(name)

    async def setup_hook(self):
        with contextlib.suppress(commands.ExtensionNotFound):
            # TODO: replace with config value
            if True:
                await self.load_extension("jishaku")

        for file in pathlib.Path('src/exts').glob('**/*.py'):
            *tree, _ = file.parts
            ext = f"{'.'.join(tree)}.{file.stem}"

            await self.load_extension(ext)

        await self.process_config()

    async def process_config(self):
        if not self.config:
            return

        for name, payload in self.config.command.items():
            await process_command(bot=self, name=name, payload=payload)

    # TODO: come up with a better name
    def defer_to_event_handlers_en_masse(self, method: str, event_handlers: set[EventHandler], *args, **kwargs):
        bot = self

        for callback in event_handlers:
            # https://github.com/Rapptz/discord.py/blob/master/discord/client.py#L450-L499
            coro = self._run_event(callback, method, bot, *args, **kwargs)

            self.loop.create_task(coro, name=f"bot: {method}")

    def _schedule_event(self, callback: Listener, method: str, *args: Any, **kwargs: Any):
        event_handlers_found = self.events.get(method, False)

        if not event_handlers_found:
            return super()._schedule_event(callback, method, *args, **kwargs)

        self.defer_to_event_handlers_en_masse(method, event_handlers_found, *args, **kwargs)

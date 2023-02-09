from __future__ import annotations

import contextlib
import logging
import pathlib
import typing

import discord
from discord.ext import commands

from src.config import Command, Config
from src.constants import STATIC_FALLBACK_PREFIX

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Coroutine

    EventHandler = Callable[[commands.Bot, *Any], Coroutine[Any, Any, Any]]
    Listener = Callable[..., Coroutine[Any, Any, Any]]

log = logging.getLogger('bot')


# TODO: bot HMR
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=STATIC_FALLBACK_PREFIX,
            intents=discord.Intents.all(),
        )

        self.config: Config | None = None
        self.event_handlers: dict[str, EventHandler] = {}

    # TODO: when typings are merged, replace Command | Group with Invokable
    def find_command(self, name: str, payload: Command) -> commands.Command | commands.Group | None:
        for command in self.walk_commands():
            if command.name not in {name, payload.name}:
                continue

            return command

    async def handle_extension_as_command(
        self, *, name: str, payload: Command, is_parent: bool = False
    ) -> commands.Command | commands.Group | None:
        cls = commands.HybridGroup if is_parent else commands.HybridCommand

        if not self.config:
            log.warning(f'No config was found, unable to process command {name}')

            return

        command_found = self.find_command(name, payload)

        if not command_found:
            return log.warning(f'Command "{name}" not found from config')

        self.remove_command(command_found.qualified_name)

        new_command = cls(
            command_found.callback,
            aliases=payload.aliases,
            help=payload.description,
            name=payload.name or name,
            invoke_without_command=True,
            disabled=payload.disabled,
            hidden=payload.hidden,
            with_app_command=payload.hybrid,
        )

        if payload.parent:
            parent = await self.handle_extension_as_command(
                name=f"{payload.parent}".strip(),
                payload=self.config.command[payload.parent],
                is_parent=True,
            )

            if isinstance(parent, commands.Group):
                parent.add_command(new_command)

        else:
            self.add_command(new_command)

        return new_command

    def add_event(self, handler: EventHandler):
        name = handler.__name__
        extension = handler.__module__
        bot = self
        handler_found = self.event_handlers.get(extension, False)

        if handler_found:
            # TODO: raise error
            return

        async def abstract_bot_parameter(*args, **kwargs):
            return await handler(bot, *args, **kwargs)

        abstract_bot_parameter.__name__ = name

        setattr(self, name, abstract_bot_parameter)
        self.event_handlers.setdefault(extension, handler)
        log.info(f"Loaded event {name}")

    async def default_on_message(self, message: discord.Message):
        await self.process_commands(message)

    def remove_event(self, handler: EventHandler):
        name = handler.__name__
        extension = handler.__module__
        handler_found = self.event_handlers.get(extension, False)

        if not handler_found:
            # TODO: raise error here
            return

        special_case_on_message_event_for_hmr = not self.on_message
        del self.event_handlers[extension]

        delattr(self, name)

        if special_case_on_message_event_for_hmr:
            self.on_message = self.default_on_message

        log.info(f"Unloaded event {name}")

    async def load_extension(self, extension: str):
        try:
            await super().load_extension(extension)
            log.info(f'Loaded extension {extension!r}')
        except Exception as error:
            log.error(f'Failed to load extension {extension!r}', exc_info=error)

    async def unload_extension(self, extension: str):
        try:
            await super().unload_extension(extension)

            event_handler_found = self.event_handlers.get(extension, False)

            if event_handler_found:
                self.remove_event(event_handler_found)

            log.info(f'Unloaded extension {extension!r}')
        except Exception as error:
            log.error(f'Failed to unload extension {extension!r}', exc_info=error)

    async def reload_extension(self, name: str) -> None:
        return await super().reload_extension(name)

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
            await self.handle_extension_as_command(name=name, payload=payload)

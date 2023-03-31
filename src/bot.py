from __future__ import annotations

import asyncio
import contextlib
import importlib
import inspect
import logging
import pathlib
import sys
import types
import typing

import discord
from discord.ext import commands
from discord.utils import MISSING

from src.config import Command, Config
from src.constants import STATIC_FALLBACK_PREFIX
from src.errors import ModuleAlreadyLoaded, ModuleError, ModuleFailed, ModuleNotFound

if typing.TYPE_CHECKING:
    import importlib.util
    from importlib.machinery import ModuleSpec
    from typing import Any

    from src.typings import EventHandler, Listener

# TODO: create multiple loggers to differentiate between loading extensions
# natively vs with Jishaku vs with custom logic
log = logging.getLogger('bot')
reloading_event = asyncio.Event()


# TODO: add shorter way to resolve names when loading/unload extensions (i.e. from name via parsing tails of paths)
# TODO: add flake8/pylint to warn for large indentation levels
class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        commands.Bot.__init__(self, command_prefix=STATIC_FALLBACK_PREFIX, intents=discord.Intents.all(), *args, **kwargs)

        self.config: Config | None = None
        self.queue: asyncio.LifoQueue | None = None
        self.event_handlers: dict[str, EventHandler] = {}
        self.wrapped_listeners: dict[str, list[Listener]] = {}

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
            log.warning(f'No config was found, unable to process command {name!r}')

            return

        command_found = self.find_command(name, payload)

        if not command_found:
            return log.warning(f'Command {name!r} not found from config')

        self.remove_command(command_found.qualified_name)

        new_command = cls(
            command_found.callback,
            aliases=payload.aliases,
            disabled=payload.disabled,
            help=payload.description,
            hidden=payload.hidden,
            invoke_without_command=True,
            name=payload.name or name,
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

    def on_module_error(self, error: ModuleError):
        log.error(error.message, exc_info=error)

    def load_module(self, module_path: str, *, spec: ModuleSpec, module: types.ModuleType):
        module_already_loaded = sys.modules.get(module_path, False)

        if module_already_loaded:
            raise ModuleAlreadyLoaded(module_path)
        elif not spec.loader:
            raise ModuleFailed(f"Loader not found for module {module_path!r}", module=module, spec=spec)

        sys.modules[module_path] = module

        try:
            spec.loader.exec_module(module)
        except Exception as error:
            raise ModuleFailed(f"Failed to load module {module_path!r}", module=module, spec=spec, original=error)

    def unload_module(self, module_path: str, *, spec: ModuleSpec, module: types.ModuleType):
        try:
            del sys.modules[module_path]

            for imported_module_name in sys.modules.keys():
                is_submodule = imported_module_name.startswith(f"{module.__name__}.")

                if is_submodule:
                    del sys.modules[imported_module_name]
        except KeyError:
            raise ModuleNotFound(f"Failed to unload module {module_path!r}", module=module, spec=spec)

    def reload_module(self, module_path: str):
        spec_found = importlib.util.find_spec(module_path)

        if not spec_found:
            raise ModuleNotFound(f"Could not find module {module_path!r}")

        module_found = importlib.util.module_from_spec(spec_found)

        if not module_found:
            raise ModuleNotFound(f"Could not find module {module_path!r}")

        try:
            self.unload_module(module_path, spec=spec_found, module=module_found)
            self.load_module(module_path, spec=spec_found, module=module_found)
        except ModuleError as error:
            self.on_module_error(error)

    def add_event(self, handler: EventHandler):
        name = handler.__name__
        extension = handler.__module__
        bot = self
        handler_found = self.event_handlers.get(extension, False)

        if handler_found:
            # FIXME: raise error
            return

        async def abstract_bot_parameter(*args, **kwargs):
            return await handler(bot, *args, **kwargs)

        abstract_bot_parameter.__name__ = name

        setattr(self, name, abstract_bot_parameter)
        self.event_handlers.setdefault(extension, handler)
        log.info(f"Loaded event {name!r}")

    async def default_on_message(self, message: discord.Message):
        await self.process_commands(message)

    def remove_event(self, handler: EventHandler):
        name = handler.__name__
        extension = handler.__module__
        handler_found = self.event_handlers.get(extension, False)

        if not handler_found:
            # FIXME: raise error
            return

        special_case_on_message_event_for_hmr = not self.on_message
        del self.event_handlers[extension]

        delattr(self, name)

        if special_case_on_message_event_for_hmr:
            self.on_message = self.default_on_message

        log.info(f"Unloaded event {name!r}")

    def add_listener(self, listener: Listener, /, name: str = MISSING):
        name = listener.__name__ if name is MISSING else name
        all_parameter_annotations: list[Any] = list(inspect.get_annotations(listener, eval_str=True).values())
        initial_parameter_annotation: type = all_parameter_annotations[0]

        if initial_parameter_annotation is not type(self):
            return super().add_listener(listener, name)

        bot = self
        wrapped_listeners = self.wrapped_listeners.setdefault(name, [])

        async def abstract_bot_parameter(*args, **kwargs):
            return await listener(bot, *args, **kwargs)

        abstract_bot_parameter.__name__ = name
        abstract_bot_parameter.__original_listener__ = listener

        wrapped_listeners.append(abstract_bot_parameter)
        super().add_listener(abstract_bot_parameter, name)

    def _find_wrapped_listener(self, listener: Listener, name: str) -> Listener | None:
        wrapped_listeners = self.wrapped_listeners.get(name) or []

        for wrapped_listener in wrapped_listeners:
            if listener == wrapped_listener.__original_listener__:
                return wrapped_listener

        return None

    def remove_listener(self, listener: Listener, /, name: str = MISSING):
        name = listener.__name__ if name is MISSING else name
        listener = self._find_wrapped_listener(listener, name) or listener

        print(self.extra_events.get(name))
        super().remove_listener(listener, name)
        print(self.extra_events.get(name))

    async def load_extension(self, extension: str):
        try:
            await super().load_extension(extension)
            log.info(f'Loaded extension {extension!r}')
        except Exception as error:
            log.error(f'Failed to load extension {extension!r}', exc_info=error)

            raise error

    async def unload_extension(self, extension: str):
        try:
            await super().unload_extension(extension)

            event_handler_found = self.event_handlers.get(extension, None)

            if event_handler_found:
                self.remove_event(event_handler_found)

            log.info(f'Unloaded extension {extension!r}')
        except Exception as error:
            log.error(f'Failed to unload extension {extension!r}', exc_info=error)

            raise error

    async def reload_extension(self, name: str):
        await self.unload_extension(name)
        await self.load_extension(name)

    async def setup_hook(self):
        with contextlib.suppress(commands.ExtensionNotFound):
            # TODO: replace with config value
            if True:
                await self.load_extension("jishaku")

        # TODO: refactor
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

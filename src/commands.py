from __future__ import annotations

import logging
import typing

from discord.ext import commands

from src.config import Command

if typing.TYPE_CHECKING:
    from src.bot import Bot

log = logging.getLogger('bot')


def find_command(bot: Bot, name: str, payload: Command) -> commands.Command | commands.Group | None:
    for command in bot.walk_commands():
        if command.name not in {name, payload.name}:
            continue

        return command


async def process_command(
    *, bot, name: str, payload: Command, is_parent: bool = False
) -> commands.Command | commands.Group | None:
    cls = commands.HybridGroup if is_parent else commands.HybridCommand

    if not bot.config:
        log.warning(f'No config was found, unable to process command {name}')

        return

    command_found = find_command(bot, name, payload)

    if not command_found:
        return log.warning(f'Command "{name}" not found from config')

    bot.remove_command(command_found.qualified_name)

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
        parent = await process_command(
            bot=bot,
            name=f"{payload.parent}".strip(),
            payload=bot.config.command[payload.parent],
            is_parent=True,
        )

        if isinstance(parent, commands.Group):
            parent.add_command(new_command)

    else:
        bot.add_command(new_command)

    return new_command

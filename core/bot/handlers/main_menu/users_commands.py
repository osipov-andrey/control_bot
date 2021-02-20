from dataclasses import asdict

from core._helpers import ArgScheme, ArgType, CommandSchema
from core.bot.handlers.actuator_commands._command import InternalCommand
from core.bot.handlers._static_commands import *
from core.bot.telegram_api import telegram_api_dispatcher as d
# TODO: Всю эту срань надо переписать


async def get_subscribe_or_unsubscribe_cmd(cmd, user_id, is_admin) -> InternalCommand:
    channels = [c.name for c in await d.observer.channels.all_channels()]
    """
    Схема команды для подписки/отписки на канал.
    Так как для этих двух действий нужны одинаковые аргументы -
    можно воспользоваться одной и той же командой.

    Собственно команда нужна для ввода аргументов с помощью того же
    механизма, которым вводятся аргументы для команд актуатора.

    Если в случае команд актуатора бизнес-логика выполняется в актуаторе,
    то для внутренних команд она выполняется (вызывается) в обработчике.
    """
    args = {
        "channel": asdict(ArgScheme(
            description="Название канала",
            schema={"type": ArgType.STR.value, "allowed": channels},
            is_channels=True
        )),
        "user_id": asdict(ArgScheme(
            description="ID пользователя",
            schema={"type": ArgType.INT.value},
            is_user=True if cmd == SUBSCRIBE else False,
            is_subscriber=True if cmd == UNSUBSCRIBE else False,
        ))
    }

    cmd_schema = CommandSchema(
                    hidden=False,
                    behavior__admin={
                        "description": "Подписать/отписать пользователя на канал",
                        "args": args,
                    },
                )

    command = InternalCommand(
            cmd,
            user_id,
            cmd_schema=cmd_schema,
            is_admin=is_admin,
        )
    return command


async def get_grant_or_revoke_cmd(cmd, user_id, is_admin) -> InternalCommand:
    actuators = [a.name for a in await d.observer.actuators.get_all()]
    args = {
        "actuator": asdict(ArgScheme(
            description="Название актуатора",
            schema={"type": ArgType.STR.value, "allowed": actuators},
            is_actuators=True,
            options=actuators,
         )),
        "user_id": asdict(ArgScheme(
            description="ID пользователя",
            schema={"type": ArgType.INT.value},
            is_user=True if cmd == GRANT else False,
            is_granter=True if cmd == REVOKE else False
        )),
    }

    cmd_schema = CommandSchema(
                    hidden=False,
                    behavior__admin={
                        "description": "Открыть/закрыть доступ к актуатору",
                        "args": args,
                    },
                )

    command = InternalCommand(
            cmd,
            user_id,
            cmd_schema=cmd_schema,
            is_admin=is_admin,
        )
    return command


def get_create_or_delete_cmd(cmd, user_id, is_admin) -> InternalCommand:
    args = {
        "actuator_name": asdict(ArgScheme(
            description="Название актуатора",
            schema={"type": ArgType.STR.value},
            is_actuators=True,
        )),
        "description": asdict(ArgScheme(
            description="Actuator description",
            schema={"type": ArgType.STR.value},
        )),
    }
    if cmd == DELETE_ACTUATOR:
        args.pop("description")
    cmd_schema = CommandSchema(
        hidden=False,
        behavior__admin={
            "description": "Create/delete_channel actuator",
            "args": args,
        },
    )

    command = InternalCommand(
        cmd,
        user_id,
        cmd_schema=cmd_schema,
        is_admin=is_admin,
    )
    return command


def get_create_or_delete_channel_cmd(cmd, user_id, is_admin) -> InternalCommand:
    args = {
        "channel_name": asdict(ArgScheme(
            description="Channel name",
            schema={"type": ArgType.STR.value},
            is_channels=True,
        )),
        "description": asdict(ArgScheme(
            description="Channel description",
            schema={"type": ArgType.STR.value},
        )),
    }
    if cmd == DELETE_CHANNEL:
        args.pop("description")
    cmd_schema = CommandSchema(
        hidden=False,
        behavior__admin={
            "description": "Create/delete_channel channel",
            "args": args,
        },
    )

    command = InternalCommand(
        cmd,
        user_id,
        cmd_schema=cmd_schema,
        is_admin=is_admin,
    )
    return command

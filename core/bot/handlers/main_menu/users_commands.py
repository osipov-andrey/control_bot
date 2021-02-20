from core._helpers import ArgScheme, ArgTypes, CommandSchema
from core.bot.handlers.actuator_commands._command import InternalCommand
from core.bot.handlers._static_commands import *
from core.bot.telegram_api import telegram_api_dispatcher as d
# TODO: Всю эту срань надо переписать


def get_subscribe_or_unsubscribe_cmd(cmd, user_id, is_admin) -> InternalCommand:
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
        "user_id": ArgScheme(
            description="ID пользователя",
            schema={"type": ArgTypes.INT.value},
            is_user=True if cmd == SUBSCRIBE else False,
            # is_subscriber=True if cmd == "unsubscribe" else False,
        )._asdict(),
        "channel": ArgScheme(
            description="Название канала",
            schema={"type": ArgTypes.STR.value}
            # TODO: options
        )._asdict()
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
        "actuator": ArgScheme(
            description="Название актуатора",
            schema={"type": ArgTypes.STR.value, "allowed": actuators},
            is_actuators=True,
            options=actuators,
         )._asdict(),
        "user_id": ArgScheme(
            description="ID пользователя",
            schema={"type": ArgTypes.INT.value},
            is_user=True if cmd == GRANT else False,
            is_granter=True if cmd == REVOKE else False
        )._asdict(),
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
        "actuator_name": ArgScheme(
            description="Название актуатора",
            schema={"type": ArgTypes.STR.value},
            is_actuators=True,
        )._asdict(),
        "description": ArgScheme(
            description="Actuator description",
            schema={"type": ArgTypes.STR.value},
        )._asdict(),
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
        "channel_name": ArgScheme(
            description="Channel name",
            schema={"type": ArgTypes.STR.value},
            # is_channels=True,
        )._asdict(),
        "description": ArgScheme(
            description="Channel description",
            schema={"type": ArgTypes.STR.value},
        )._asdict(),
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

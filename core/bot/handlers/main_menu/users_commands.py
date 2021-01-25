from core._helpers import ArgScheme, ArgTypes, CommandSchema
from core.bot.handlers.actuator_commands._command import InternalCommand


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
            is_user=True if cmd == "subscribe" else False,
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


# def get_unsubscribe_cmd(cmd, user_id, is_admin) -> InternalCommand:
#
#     args = {
#         "user_id": ArgScheme(
#             description="ID пользователя",
#             schema={"type": ArgTypes.INT.value},
#             is_subscriber=True
#         )._asdict(),
#         "channel": ArgScheme(
#             description="Название канала",
#             schema={"type": ArgTypes.STR.value}
#         )._asdict()
#     }
#
#     cmd_schema = CommandSchema(
#                     hidden=False,
#                     behavior__admin={
#                         "description": "Отписать пользователя от канала",
#                         "args": args,
#                     },
#                 )
#
#     unsubscribe_cmd = InternalCommand(
#             cmd,
#             user_id,
#             cmd_schema=cmd_schema,
#             is_admin=is_admin,
#         )
#     return unsubscribe_cmd


def get_grant_or_revoke_cmd(cmd, user_id, is_admin) -> InternalCommand:

    args = {
        "user_id": ArgScheme(
            description="ID пользователя",
            schema={"type": ArgTypes.INT.value},
            is_user=True if cmd == "grant" else False
        )._asdict(),
        "actuator": ArgScheme(
            description="Название актуатора",
            schema={"type": ArgTypes.STR.value}
        )._asdict()
    }

    cmd_schema = CommandSchema(
                    hidden=False,
                    behavior__admin={
                        "description": "Открыть/закрыть доступ к актуатору",
                        "args": args,
                        # TODO: options
                    },
                )

    command = InternalCommand(
            cmd,
            user_id,
            cmd_schema=cmd_schema,
            is_admin=is_admin,
        )
    return command

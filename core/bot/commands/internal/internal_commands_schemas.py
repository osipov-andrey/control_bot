"""
Module with raw command schemes for using in main menu without actuators.
This InternalCommands use the same workflow, like taken from actuator schemes.

If in case of actuator commands we write business logic in the actuator,
then in this case we write logic in the message handlers.
"""

from core._helpers import ArgType
from core.inbox.models import ArgInfo, CommandSchema
from core.bot.commands.internal.internal_command import InternalCommand
from core.bot._command_constants import (
    SUBSCRIBE,
    GRANT,
    REVOKE,
    DELETE_ACTUATOR,
    DELETE_CHANNEL,
    UNSUBSCRIBE,
)
from core.mediator.dependency import MediatorDependency


async def get_subscribe_or_unsubscribe_cmd(cmd, user_id, is_admin) -> InternalCommand:
    """ Generate schema for subscribe/unsubscribe main-menu commands """
    channels = [
        c.name for c in await MediatorDependency.mediator.channels.all_channels()
    ]

    args = {
        "channel": ArgInfo(
            description="Channel name",
            arg_schema={"type": ArgType.STR.value, "allowed": channels},
            is_channel=True,
        ).dict(),
        "user_id": ArgInfo(
            description="Telegram user ID",
            arg_schema={"type": ArgType.INT.value},
            is_user=(cmd == SUBSCRIBE),
            is_subscriber=(cmd == UNSUBSCRIBE),
        ).dict(),
    }

    cmd_schema = CommandSchema(
        hidden=False,
        behavior__admin={
            "description": "Subscribe/unsubscribe user to channel",
            "args": args,
        },
    )

    command = InternalCommand(cmd, user_id, cmd_schema=cmd_schema, is_admin=is_admin)
    return command


async def get_grant_or_revoke_cmd(cmd, user_id, is_admin) -> InternalCommand:
    """ Generate schema for grant/revoke main-menu commands """
    actuators = [a.name for a in await MediatorDependency.mediator.actuators.get_all()]
    args = {
        "actuator": ArgInfo(
            description="Actuator name",
            arg_schema={"type": ArgType.STR.value, "allowed": actuators},
            is_actuator=True,
            options=actuators,
        ).dict(),
        "user_id": ArgInfo(
            description="Telegram user ID",
            arg_schema={"type": ArgType.INT.value},
            is_user=(cmd == GRANT),
            is_granter=(cmd == REVOKE),
        ).dict(),
    }

    cmd_schema = CommandSchema(
        hidden=False,
        behavior__admin={
            "description": "Grant/revoke the user rights to the drive",
            "args": args,
        },
    )

    command = InternalCommand(cmd, user_id, cmd_schema=cmd_schema, is_admin=is_admin)
    return command


def get_create_or_delete_cmd(cmd, user_id, is_admin) -> InternalCommand:
    """ Generate schema for create/delete actuator main-menu commands """
    args = {
        "actuator": ArgInfo(
            description="Actuator name",
            arg_schema={"type": ArgType.STR.value},
            is_actuator=True,
        ).dict(),
        "description": ArgInfo(
            description="Actuator description", arg_schema={"type": ArgType.STR.value}
        ).dict(),
    }
    if cmd == DELETE_ACTUATOR:
        args.pop("description")
    cmd_schema = CommandSchema(
        hidden=False,
        behavior__admin={"description": "Create/delete actuator", "args": args},
    )

    command = InternalCommand(cmd, user_id, cmd_schema=cmd_schema, is_admin=is_admin)
    return command


def get_create_or_delete_channel_cmd(cmd, user_id, is_admin) -> InternalCommand:
    """ Generate schema for create/delete channel main-menu commands """
    args = {
        "channel": ArgInfo(
            description="Channel name",
            arg_schema={"type": ArgType.STR.value},
            is_channel=True,
        ).dict(),
        "description": ArgInfo(
            description="Channel description", arg_schema={"type": ArgType.STR.value}
        ).dict(),
    }
    if cmd == DELETE_CHANNEL:
        args.pop("description")
    cmd_schema = CommandSchema(
        hidden=False,
        behavior__admin={"description": "Create/delete channel", "args": args},
    )

    command = InternalCommand(cmd, user_id, cmd_schema=cmd_schema, is_admin=is_admin)
    return command

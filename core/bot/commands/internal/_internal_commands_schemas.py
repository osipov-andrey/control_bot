"""
Module with raw command schemes for using in main menu without actuators.
This InternalCommands use the same workflow, like taken from actuator schemes.

If in case of actuator commands we write business logic in the actuator,
then in this case we write logic in the message handlers.
"""
from dataclasses import asdict

from core._helpers import ArgScheme, ArgType, CommandSchema
from core.bot.commands.internal._internal_command import InternalCommand
from core.bot._command_constants import *
from core.mediator.dependency import MediatorDependency


async def get_subscribe_or_unsubscribe_cmd(cmd, user_id, is_admin) -> InternalCommand:
    channels = [c.name for c in await MediatorDependency.mediator.channels.all_channels()]

    args = {
        "channel": asdict(ArgScheme(
            description="Channel name",
            schema={"type": ArgType.STR.value, "allowed": channels},
            is_channel=True
        )),
        "user_id": asdict(ArgScheme(
            description="Telegram user ID",
            schema={"type": ArgType.INT.value},
            is_user=True if cmd == SUBSCRIBE else False,
            is_subscriber=True if cmd == UNSUBSCRIBE else False,
        ))
    }

    cmd_schema = CommandSchema(
        hidden=False,
        behavior__admin={
            "description": "Subscribe/unsubscribe user to channel",
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
    actuators = [a.name for a in await MediatorDependency.mediator.actuators.get_all()]
    args = {
        "actuator": asdict(ArgScheme(
            description="Actuator name",
            schema={"type": ArgType.STR.value, "allowed": actuators},
            is_actuator=True,
            options=actuators,
        )),
        "user_id": asdict(ArgScheme(
            description="Telegram user ID",
            schema={"type": ArgType.INT.value},
            is_user=True if cmd == GRANT else False,
            is_granter=True if cmd == REVOKE else False
        )),
    }

    cmd_schema = CommandSchema(
        hidden=False,
        behavior__admin={
            "description": "Grant/revoke the user rights to the drive", # TODO
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
        "actuator": asdict(ArgScheme(
            description="Actuator name",
            schema={"type": ArgType.STR.value},
            is_actuator=True,
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
            "description": "Create/delete actuator",
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
        "channel": asdict(ArgScheme(
            description="Channel name",
            schema={"type": ArgType.STR.value},
            is_channel=True,
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
            "description": "Create/delete channel",
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

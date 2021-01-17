from core._helpers import ArgScheme, ArgTypes, CommandSchema
from core.bot.handlers.actuator_commands._command import InternalCommand


def get_subscribe_cmd(cmd, user_id, is_admin) -> InternalCommand:

    args = {
        "user_id": ArgScheme(
            description="ID пользователя",
            schema={"type": ArgTypes.INT.value},
            is_user=True
        )._asdict(),
        "channel": ArgScheme(
            description="Название канала",
            schema={"type": ArgTypes.STR.value}
        )._asdict()
    }

    cmd_schema = CommandSchema(
                    hidden=False,
                    behavior__admin={
                        "description": "Подписать пользователя на канал",
                        "args": args,
                    },
                )

    subscribe_cmd = InternalCommand(
            cmd,
            user_id,
            cmd_schema=cmd_schema,
            is_admin=is_admin,
        )
    return subscribe_cmd

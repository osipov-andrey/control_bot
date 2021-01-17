from core._helpers import ArgScheme, CommandSchema
from core.bot.handlers.actuator_commands._command import InternalCommand


def get_subscribe_cmd(cmd, user_id, is_admin) -> InternalCommand:
    subscribe_cmd = InternalCommand(
            cmd,
            user_id,
            cmd_schema=CommandSchema(
                hidden=False,
                behavior__admin={
                    "description": "Подписать пользователя на канал",
                    "args": {
                        "user": ArgScheme("ID пользователя", {"type": "string"})._asdict(),
                        "channel": ArgScheme("Название канала", {"type": "string"})._asdict()
                    },
                },
            ),
            is_admin=is_admin,
        )
    return subscribe_cmd

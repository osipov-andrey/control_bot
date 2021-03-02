from typing import Optional

from core._helpers import Behavior, CommandBehavior, CommandSchema
from core.bot.commands.actuator.actuator_command import ActuatorCommand


class InternalCommand(ActuatorCommand):
    """ The command spawned inside the bot """

    def __init__(
            self, cmd: str, user_id: int, cmd_schema: CommandSchema, arguments: Optional[list] = None, is_admin=False
    ):  # pylint: disable=super-init-not-called

        if is_admin and cmd_schema.behavior__admin:
            self.cmd_scheme: CommandBehavior = cmd_schema.behavior__admin
            self.behavior = Behavior.ADMIN.value
        elif cmd_schema.behavior__user:
            self.cmd_scheme = cmd_schema.behavior__user
            self.behavior = Behavior.USER.value
        else:  # Такой команды нет, или она admin_only_func:
            return
        self.cmd = cmd
        self.user_id = user_id
        self.list_args: list = arguments if arguments else []
        self.filled_args = dict()
        self.args_to_fill = list()

        self.validation_errors = dict()

        self._parse_args_to_fill()

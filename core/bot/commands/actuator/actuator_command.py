from itertools import zip_longest
from uuid import UUID

from typing import Optional, List, Union

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from cerberus import Validator

from core.bot._notification_constants import CONTEXT_CANCEL_MENU
from core._helpers import ArgType, Behavior
from core.inbox.models import ArgInfo, CommandBehavior, CommandSchema
from core.bot.state_enums import ArgumentsFillStatus
from core.bot._prompts_generators import generate_prompt
from core.mediator.dependency import MediatorDependency as md


class ActuatorCommand:
    """Команда, полученная из телеги"""

    @staticmethod
    def parse_cmd_string(cmd_string: str):
        """Split command macros"""
        assert cmd_string.startswith("/")

        full_cmd = cmd_string.split("_")
        client = full_cmd[0][1:]
        try:
            cmd: Optional[str] = full_cmd[1]
        except IndexError:
            cmd = None
        args = full_cmd[2:]

        return client, cmd, args

    def __init__(
        self,
        client: str,
        cmd: str,
        arguments: List,
        user_id: int,
        is_admin=False,
        message_id: Optional[UUID] = None,
    ):

        self.client = client
        self.cmd: str = cmd
        self.user_id = user_id
        self.message_id = message_id
        self.behavior = Behavior.USER.value

        cmd_info: CommandSchema = md.get_mediator().actuators.get_command_info(client, cmd)
        if is_admin and cmd_info.behavior__admin:
            self.cmd_scheme: CommandBehavior = cmd_info.behavior__admin
            self.behavior = Behavior.ADMIN.value
        elif cmd_info.behavior__user:
            self.cmd_scheme = cmd_info.behavior__user
        else:  # Такой команды нет, или она admin_only_func:
            return

        self.list_args: list = arguments
        self.filled_args: dict = dict()
        self.args_to_fill: list = list()

        self.validation_errors: dict = dict()

        self._parse_args_to_fill()

    @property
    def fill_status(self):
        if len(self.args_to_fill) == 0:
            return ArgumentsFillStatus.FILLED
        return ArgumentsFillStatus.NOT_FILLED

    def fill_argument(self, arg_value):
        arg_name = self.args_to_fill.pop(0)
        arg_scheme = self._get_arg_scheme(arg_name)

        if arg_scheme.arg_schema.type == ArgType.LIST.value:
            self.filled_args[arg_name] = arg_value.split(" ")
            return

        validated = self._validate_arg(arg_name, arg_scheme, arg_value)

        if validated:
            self.filled_args[arg_name] = arg_value
        else:
            self.args_to_fill.insert(0, arg_name)

    async def get_next_step(self) -> dict:
        message_kwargs = dict()
        argument_to_fill = self.args_to_fill[0]
        argument_info: ArgInfo = self._get_arg_scheme(argument_to_fill)
        options = argument_info.options
        if options:
            message_kwargs["reply_markup"] = self._generate_keyboard(options)
        message = ""
        if self.validation_errors:
            message += self._get_validation_report()
        prompt = await generate_prompt(argument_info, self.filled_args)
        message += (
            f"Fill in the following <b>{self.cmd}</b> argument:\n"
            f"<i><b>{argument_to_fill}</b></i> - {argument_info.description}\n"
            f"{prompt if prompt else ''}"
        )

        message_kwargs["text"] = message + CONTEXT_CANCEL_MENU
        return message_kwargs

    # fmt: off
    def _get_validation_report(self) -> str:
        report = (
            "<b>The following arguments were entered with errors:</b>\n"
            + "\n".join(
                f"{arg}: {error}"
                for arg, error in self.validation_errors.items()
            )
            + "\n\n"
        )
        return report

    # fmt: on

    @staticmethod
    def _generate_keyboard(options: list) -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for option in options:
            keyboard.insert(KeyboardButton(option))
        return keyboard

    def _parse_args_to_fill(self):
        """Compare Received and Required Arguments"""
        required_args = list(self.cmd_scheme.args.keys())

        for index, (required_arg, received_value) in enumerate(
            zip_longest(required_args, self.list_args)
        ):
            if not required_arg:
                break
            if received_value:
                arg_info = self._get_arg_scheme(required_arg)

                if arg_info.arg_schema.type == ArgType.LIST.value:
                    # Если тип аргумента лист - то все,
                    # что есть далее в полученных аргументах - запихиваем в лист
                    self.filled_args[required_arg] = self.list_args[index:]
                    break
                    # лист может быть только в конце аргументов

                validated = self._validate_arg(required_arg, arg_info, received_value)
                if validated:
                    self.filled_args[required_arg] = received_value
                else:
                    self.args_to_fill.append(required_arg)
            else:
                self.args_to_fill.append(required_arg)

    def _validate_arg(
        self, arg_name: str, arg_info: ArgInfo, received_value: Union[int, str]
    ) -> bool:
        if arg_info.arg_schema.type == ArgType.INT.value:
            try:  # Телеграм возвращает всегда строки
                received_value = int(received_value)
            except ValueError:
                pass  # Цербер скажет это за меня
        v = Validator({arg_name: arg_info.arg_schema.dict()})
        validation = v.validate({arg_name: received_value})
        if validation is False:
            self.validation_errors.update(v.errors)
        else:
            if arg_name in self.validation_errors:
                self.validation_errors.pop(arg_name)
        return bool(validation)

    def _get_arg_scheme(self, arg_name: str) -> ArgInfo:
        arg_info: Optional[ArgInfo] = self.cmd_scheme.args.get(arg_name)
        if not arg_info:
            raise RuntimeError(f"There is no ArgInfo for {self.cmd_scheme}!")
        return arg_info

    def __str__(self):
        return (
            f"{self.__class__.__name__}: "
            f"(cmd={self.cmd}; args={self.list_args}; user-id={self.user_id})"
        )

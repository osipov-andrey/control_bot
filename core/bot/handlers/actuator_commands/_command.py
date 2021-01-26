from itertools import zip_longest
from uuid import UUID

from typing import Optional, List, Union

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from cerberus import Validator

from core.bot.constant_strings import CONTEXT_CANCEL_MENU
from core.bot.telegram_api import telegram_api_dispatcher
from core._helpers import ArgScheme, ArgTypes, Behaviors, CommandBehavior, CommandSchema
from core.bot.state_enums import ArgumentsFillStatus
from core.local_storage.schema import Actuator, User


class TelegramBotCommand:
    """ Команда, полученная из телеги """

    @staticmethod
    def parse_cmd_string(cmd_string: str):
        assert cmd_string.startswith('/')

        full_cmd = cmd_string.split('_')
        client = full_cmd[0][1:]
        try:
            cmd = full_cmd[1]
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
            message_id: Optional[UUID] = None):

        self.client = client
        self.cmd: str = cmd
        self.user_id = user_id
        self.message_id = message_id
        self.behavior = Behaviors.USER.value
        # self.OBSERVER = telegram_api_dispatcher.observer

        cmd_info: CommandSchema = telegram_api_dispatcher.observer.actuators.get_command_info(client, cmd)
        if is_admin and cmd_info.behavior__admin:
            self.cmd_scheme: CommandBehavior = cmd_info.behavior__admin
            self.behavior = Behaviors.ADMIN.value
        elif cmd_info.behavior__user:
            self.cmd_scheme = cmd_info.behavior__user
        else:  # Такой команды нет, или она admin_only:
            return

        self.list_args: list = arguments
        self.filled_args = dict()
        self.args_to_fill = list()

        self.validation_errors = dict()

        self._parse_args_to_fill()

    @property
    def fill_status(self):
        if len(self.args_to_fill) == 0:
            return ArgumentsFillStatus.FILLED
        else:
            return ArgumentsFillStatus.NOT_FILLED

    def fill_argument(self, arg_value):
        arg_name = self.args_to_fill.pop(0)
        arg_scheme = self._get_arg_scheme(arg_name)

        if arg_scheme.schema['type'] == ArgTypes.LIST.value:
            self.filled_args[arg_name] = arg_value.split(' ')
            return

        validated = self._validate_arg(arg_name, arg_scheme, arg_value)

        if validated:
            self.filled_args[arg_name] = arg_value
        else:
            # TODO результат валидации в список с ошибками валидации
            self.args_to_fill.insert(0, arg_name)

    async def get_next_step(self) -> dict:
        prompt = ""
        message_kwargs = dict()
        argument_to_fill = self.args_to_fill[0]
        argument_info = self.cmd_scheme.args.get(argument_to_fill)

        options = argument_info.options
        if options:
            message_kwargs["reply_markup"] = self._generate_keyboard(options)

        message = ""
        if self.validation_errors:
            message += self._get_validation_report()
        if argument_info.is_user:
            prompt = await self._get_users_prompt()
        elif argument_info.is_actuators:
            prompt = await self._get_actuators_prompt()
        elif argument_info.is_subscriber:
            prompt = await self._get_subscribers_prompt()
        message += \
            f"Заполните следующий аргумент  команды <b>{self.cmd}</b>:\n" \
            f"<i><b>{argument_to_fill}</b></i> - {argument_info.description}\n" \
            f"{prompt if prompt else ''}" \
            f"{CONTEXT_CANCEL_MENU}"

        message_kwargs["text"] = message
        return message_kwargs

    async def _get_actuators_prompt(self):
        prompt = "<b>Зарегистрированные в боте актуаторы:</b>\n"
        actuators: List[Actuator] = await telegram_api_dispatcher.observer.actuators.get_all()
        if actuators:
            prompt += "".join(
                f"/{actuator.name} - {actuator.description}\n"
                for actuator in actuators
            )
        else:
            prompt += "Нет зарегистрированных актуаторов"
        return prompt

    async def _get_users_prompt(self) -> str:
        prompt = "<b>Зарегистрированные в боте пользователи:</b>\n"
        users: List[User] = await telegram_api_dispatcher.observer.users.get_all()
        if users:
            prompt += "".join(f"/{user.telegram_id} - {user.name}\n" for user in users)
        else:
            prompt += "Нет зарегистрированных пользователей"
        return prompt

    async def _get_subscribers_prompt(self, channel: str) -> str:
        """ Получить справку по подписчикам канала """
        subscribers = await telegram_api_dispatcher.observer.channels.get_subscribers(channel)

    def _get_validation_report(self) -> str:
        report = "<b>Следующие аргументы введены с ошибками:</b>\n" \
                 + "\n".join(f"{arg}: {error}" for arg, error in self.validation_errors.items()) \
                 + "\n\n"
        return report

    @staticmethod
    def _generate_keyboard(options: list) -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for option in options:
            keyboard.insert(KeyboardButton(option))
        return keyboard

    def _parse_args_to_fill(self):
        """ Сравнить полученные аргументы и требуемые """
        required_args = list(self.cmd_scheme.args.keys())

        for index, (required_arg, received_value) in enumerate(
                zip_longest(required_args, self.list_args)
        ):
            if not required_arg:
                break
            if received_value:
                arg_scheme = self._get_arg_scheme(required_arg)

                if arg_scheme.schema['type'] == ArgTypes.LIST.value:
                    # Если тип аргумента лист - то все,
                    # что есть далее в полученных аргументах - запихиваем в лист
                    self.filled_args[required_arg] = self.list_args[index:]
                    break
                    # лист может быть только в конце аргументов

                validated = self._validate_arg(required_arg, arg_scheme, received_value)
                if validated:
                    self.filled_args[required_arg] = received_value
                else:
                    self.args_to_fill.append(required_arg)
            else:
                self.args_to_fill.append(required_arg)

    def _validate_arg(
            self,
            arg_name: str,
            arg_info: ArgScheme,
            received_value: Union[int, str]
    ) -> bool:
        if arg_info.schema['type'] == ArgTypes.INT.value:
            try:  # Телеграм возвращает всегда строки
                received_value = int(received_value)
            except ValueError:
                pass  # Цербер скажет это за меня
        v = Validator({arg_name: arg_info.schema})
        validation = v.validate({arg_name: received_value})
        if validation is False:
            self.validation_errors.update(v.errors)
        else:
            if arg_name in self.validation_errors:
                self.validation_errors.pop(arg_name)
        return validation

    def _get_arg_scheme(self, arg_name: str) -> ArgScheme:
        return self.cmd_scheme.args.get(arg_name)

    # def __repr__(self):
    #     return f"{self.__class__.__name__}"\
    #            f"(full_cmd=\"{self._full_cmd}\", user-id=\"{self.user_id}\")"

    def __str__(self):
        return f"{self.__class__.__name__}: " \
               f"(cmd={self.cmd}; args={self.list_args}; user-id={self.user_id})"


class InternalCommand(TelegramBotCommand):
    """ Команда, порожденная внутри бота """

    def __init__(self, cmd: str, user_id: int, cmd_schema: CommandSchema, arguments: Optional[list] = None, is_admin=False):
        # self.OBSERVER = telegram_api_dispatcher.observer
        if is_admin and cmd_schema.behavior__admin:
            self.cmd_scheme: CommandBehavior = cmd_schema.behavior__admin
            self.behavior = Behaviors.ADMIN.value
        elif cmd_schema.behavior__user:
            self.cmd_scheme = cmd_schema.behavior__user
            self.behavior = Behaviors.USER.value
        else:  # Такой команды нет, или она admin_only:
            return
        self.cmd = cmd
        self.user_id = user_id
        self.list_args: list = arguments if arguments else []
        self.filled_args = dict()
        self.args_to_fill = list()

        self.validation_errors = dict()

        self._parse_args_to_fill()

"""
TgAPI --(cmd)--> Handler --(event)--> Observer
"""
from itertools import zip_longest
from uuid import UUID

import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from typing import Optional, List

from aiogram.types import Message

from core._helpers import CommandScheme, MessageTarget
from core.bot.constant_strings import COMMAND_IS_NOT_FILLED, CONTEXT_CANCEL_MENU
from core.bot.state_enums import ArgumentsFillStatus, CommandFillStatus
from core.bot.states import Command
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.bot.template_strings import COMMAND_IS_NOT_EXIST, NO_SUCH_CLIENT
from core.memory_storage import NoSuchClient, NoSuchCommand
from core.sse.sse_event import SSEEvent

_COMMAND_REGEX = r"^\/([^_]*)_?.*?$"


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
            message_id: Optional[UUID] = None):

        self.client = client
        self.cmd: str = cmd
        self.user_id = user_id
        self.message_id = message_id

        self.cmd_scheme: CommandScheme = d.observer.get_command_info(client, cmd)

        self.list_args: list = arguments
        self.filled_args = dict()
        self.args_to_fill = list()

        self._parse_args_to_fill()

    def _parse_args_to_fill(self):
        """ Сравнить полученные аргументы и требуемые """
        required_args = list(self.cmd_scheme.args.keys())

        for required_arg, received_value in zip_longest(required_args, self.list_args):
            if received_value:
                self.filled_args[required_arg] = received_value
            elif not required_arg:
                break
            else:
                self.args_to_fill.append(required_args)

    @property
    def fill_status(self):
        if len(self.args_to_fill) == 0:
            return ArgumentsFillStatus.FILLED
        else:
            return ArgumentsFillStatus.NOT_FILLED

    # def __repr__(self):
    #     return f"{self.__class__.__name__}"\
    #            f"(full_cmd=\"{self._full_cmd}\", user-id=\"{self.user_id}\")"

    def __str__(self):
        return f"{self.__class__.__name__}: " \
               f"(cmd={self.cmd}; args={self.list_args}; user-id={self.user_id})"


@d.message_handler(regexp=_COMMAND_REGEX)
async def commands_handler(message: types.Message, state: FSMContext):
    print(message)
    await process_command_workflow(message, state)


async def process_command_workflow(message, state, message_id=None):
    command_state = await state.get_state()
    user_id = chat_id = message.chat.id

    message_kwargs = {'chat_id': chat_id}

    client, command, args = TelegramBotCommand.parse_cmd_string(message.text)


    # TODO проверкар прав пользователя на клиента
    # if not db.grants.has_access(client_name, user_id):
    #     return
    # TODO is_admin?
    # is_admin = db.superuser.is_admin(user_id)
    is_admin = False

    if command is None and command_state is None:
        # Пришло только имя клиента - показываем возможные команды
        message_kwargs["text"] = get_client_commands(client, is_admin)
        await d.observer.send_message_to_user(**message_kwargs)
        await Command.client.set()
        # TODO for what?
        # await storage.update_data(
        #     user=user_id,
        #     chat=chat_id,
        #     client=client_name,
        # )
        await Command.command.set()
        return
    elif command is None and command_state is not None:
        # Не указана команда
        message_kwargs["text"] = COMMAND_IS_NOT_FILLED + CONTEXT_CANCEL_MENU
        await d.observer.send_message_to_user(**message_kwargs)
        return

    exception = False
    try:
        cmd = TelegramBotCommand(client, command, args, user_id)
    except NoSuchCommand as e:
        exception = True
        message_kwargs["text"] = COMMAND_IS_NOT_EXIST.format(command=e.cmd)
    except NoSuchClient:
        exception = True
        message_kwargs["text"] = NO_SUCH_CLIENT.format(client=client)
    finally:
        if exception:
            await d.observer.send_message_to_user(**message_kwargs)
            await state.reset_state()
            return

    await continue_workflow(
        state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND
    )


async def continue_workflow(state, cmd: TelegramBotCommand, message_kwargs, fill_status):
    cmd_fill_status = cmd.fill_status

    if cmd_fill_status == ArgumentsFillStatus.FILLED:
        # Команда заполнена
        await end_workflow(state, cmd)


async def end_workflow(state, cmd: TelegramBotCommand):
    await state.reset_state()
    event = SSEEvent(
        command=cmd.cmd,
        target=MessageTarget(target_type="user", target_name=cmd.user_id),
        args=cmd.filled_args
    )
    await d.observer.emit_event(cmd.client, event)


def get_client_commands(client_name: str, is_admin=False) -> str:
    commands = d.observer.get_client_info(client_name)
    message = "Информация о командах:\n"
    for cmd in commands.values():
        if not cmd.hidden:
            if (is_admin and cmd.admin_only) or not cmd.admin_only:
                message += f"{cmd.description}\n"
    message += "\n/cancel - Выход в главное меню\n"
    return message


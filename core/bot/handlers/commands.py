"""
TgAPI --(cmd)--> Handler --(event)--> Observer
"""
import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget
from core.bot.constant_strings import COMMAND_IS_NOT_FILLED, CONTEXT_CANCEL_MENU
from core.bot.state_enums import CommandFillStatus
from core.bot.states import Command
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.bot.template_strings import COMMAND_IS_NOT_EXIST
from core.sse.sse_event import SSEEvent

_COMMAND_REGEX = r"^\/([^_]*)_?.*?$"


class TelegramBotCommand:
    """ Команда, полученная из телеги """

    def __init__(self, full_cmd: str, user_id: int):

        assert full_cmd.startswith('/')

        full_cmd = full_cmd.split('_')
        client = full_cmd[0]
        try:
            cmd = full_cmd[1]
        except IndexError:
            cmd = None
        args = full_cmd[2:]

        self.client: str = client[1:]
        self.cmd: str = cmd
        self.list_args: list = args
        self.dict_args = dict()
        self.user_id = user_id
        self._full_cmd = full_cmd

    def __repr__(self):
        return f"{self.__class__.__name__}"\
               f"(full_cmd=\"{self._full_cmd}\", user-id=\"{self.user_id}\")"

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

    message_kwargs = {'chat_id': chat_id, 'parse_mode': 'HTML'}

    cmd = TelegramBotCommand(message.text, user_id)

    # TODO проверкар прав пользователя на клиента
    # if not db.grants.has_access(client_name, user_id):
    #     return
    # TODO is_admin?
    # is_admin = db.superuser.is_admin(user_id)
    is_admin = False

    if cmd.cmd is None and command_state is None:
        # Пришло только имя клиента - показываем возможные команды
        message_kwargs["text"] = get_client_commands(cmd.client, is_admin)
        await d.observer.send_message_to_user(**message_kwargs)
        await Command.client.set()
        # TODO for what?
        # await storage.update_data(
        #     user=user_id,
        #     chat=chat_id,
        #     client=client_name,
        # )
        await Command.command.set()
    elif cmd.cmd is None and command_state is not None:
        # Не указана команда
        message_kwargs["text"] = COMMAND_IS_NOT_FILLED + CONTEXT_CANCEL_MENU
        await d.observer.send_message_to_user(**message_kwargs)
    else:
        cmd_info = d.observer.get_command_info(cmd.client, cmd.cmd)
        if not cmd_info:
            message_kwargs["text"] = COMMAND_IS_NOT_EXIST.format(command=cmd.cmd)
            d.observer.send_message_to_user(**message_kwargs)
        else:
            await continue_workflow(
                state, cmd, cmd_info, message_kwargs, CommandFillStatus.FILL_COMMAND
            )


async def continue_workflow(state, cmd, cmd_info, message_kwargs, fill_status):
    pass


def get_client_commands(client_name: str, is_admin=False) -> str:
    commands = d.observer.get_client_info(client_name)
    message = "Информация о командах:\n"
    for cmd in commands.values():
        if not cmd.hidden:
            if (is_admin and cmd.admin_only) or not cmd.admin_only:
                message += f"{cmd.description}\n"
    message += "\n/cancel - Выход в главное меню\n"
    return message


"""
TgAPI --(cmd)--> Handler --(event)--> Observer
"""
import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget
from core.bot.telegram_api import telegram_api_dispatcher as d
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
    cmd = TelegramBotCommand(message.text, message.chat.id)

    prepare_command(cmd)

    event = SSEEvent(
        command=cmd.cmd,
        args=cmd.dict_args,
        target=MessageTarget(target_type="user", target_name=cmd.user_id)
    )

    bad_result = await d.observer.emit_event(cmd.client, event)
    if bad_result:
        await message.answer(f"Something wrong: {bad_result}")


def prepare_command(cmd: TelegramBotCommand):
    command_info = d.observer.get_command_info(cmd.client, cmd.cmd)
    pass
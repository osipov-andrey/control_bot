import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot.telegram_api import telegram_api_dispatcher as d


_COMMAND_REGEX = r"^\/([^_]*)_?.*?$"


class TelegramBotCommand:

    def __init__(self, full_cmd: str, from_user: aiogram.types.User):

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
        self.args: list = args
        self.from_user = from_user
        self._full_cmd = full_cmd

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"(full_cmd=\"{self._full_cmd}\", from_user=\"{self.from_user}\")"

    def __str__(self):
        return f"{self.__class__.__name__}: " \
               f"(cmd=[{self.cmd}]; args=[{self.args}]; " \
               f"user=[{self.from_user.username} ({self.from_user.id})])"


@d.message_handler(regexp=_COMMAND_REGEX)
async def commands_handler(message: types.Message, state: FSMContext):
    print(message)
    await process_command_workflow(message, message.text, state)


async def process_command_workflow(message, text, state, message_id=None):
    pass

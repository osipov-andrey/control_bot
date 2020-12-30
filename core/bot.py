import asyncio
import aiogram
import logging

from collections import namedtuple

from core.config import config
from core.sse_server import create_sse_server
from core.inbox.consumer import RabbitConsumer

MenuCommand = namedtuple("MenuCommand", "cmd, description")
_LOGGER = logging.getLogger(__name__)
API_TOKEN = config["API_TOKEN"]


class TelegramBotMessage:

    def __init__(self, full_cmd: str, from_user: aiogram.types.User):
        full_cmd = full_cmd.split('_')
        client, cmd, args = full_cmd[0], full_cmd[1], full_cmd[2:]

        self.client: str = client[1:]
        self.cmd: str = cmd
        self.args: list = args
        self.from_user = from_user


class ControlBot:
    MAIN_MENU = (
        MenuCommand("help", "справка по командам бота"),
        MenuCommand("me", "My telegram ID"),
    )

    def __init__(self, observer: 'Observer'):
        self.observer = observer
        self.bot = aiogram.Bot(token=API_TOKEN)
        self.db = aiogram.Dispatcher(bot=self.bot)

        self.db.message_handler()(self.various_cmd_handler)

    async def various_cmd_handler(self, message: aiogram.types.Message):

        main_command = message.text.split('_')[0][1:]
        if main_command in self.observer.active_clients:
            bot_message = TelegramBotMessage(message.text, message.from_user)
            result = await self.observer.handle_command(bot_message)
            await message.reply(result)
        elif main_command == "getAvailableMethods":
            return
        else:
            result = await self.main_menu_handler(main_command)
            await message.reply(result)

    async def main_menu_handler(self, cmd):
        if cmd == "help":
            return self.main_menu

        return "main_kekos"

    @property
    def main_menu(self):
        return "\n".join(f"/{command.cmd} - {command.description}"
                         for command in self.MAIN_MENU)


class Observer:

    def __init__(self):
        self._rabbit_inbox = asyncio.Queue()

        self.rabbit = RabbitConsumer(
            **config["rabbit"],
            inbox_queue=self._rabbit_inbox,
        )
        self.sse_server = create_sse_server(self)
        self.bot = ControlBot(self)

        self.active_clients = dict()

    def run(self):
        asyncio.ensure_future(self.rabbit.listen_to_rabbit())
        asyncio.ensure_future(self.message_consumer())
        aiogram.executor.start_polling(self.bot.db, skip_updates=True)

    async def message_consumer(self):
        while True:
            message = await self._rabbit_inbox.get()
            self._rabbit_inbox.task_done()
            _LOGGER.info("Get message: %s", message)

    async def handle_command(self, message: TelegramBotMessage) -> str:
        print("handle: ", message.cmd)
        return "kekos"

    def add_client(self, client_name: str):
        queue = asyncio.Queue()
        self.active_clients[client_name] = queue
        return queue

    def remove_client(self, client_name: str):
        client_queue: asyncio.Queue = self.active_clients.pop(client_name)


import asyncio
import aiogram
import logging

from collections import namedtuple

from core.config import config
from core.sse.sse_event import SSEEvent
from core.sse.sse_server import create_sse_server
from core.inbox.consumer import RabbitConsumer
from core._helpers import get_log_cover

MenuCommand = namedtuple("MenuCommand", "cmd, description")
_LOGGER = logging.getLogger(__name__)
API_TOKEN = config["API_TOKEN"]


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


class ControlBot:
    MAIN_MENU = [
        MenuCommand("help", "справка по командам бота"),
        MenuCommand("me", "My telegram ID"),
    ]

    def __init__(self, observer: 'Observer'):
        self.observer = observer
        self.bot = aiogram.Bot(token=API_TOKEN)
        self.db = aiogram.Dispatcher(bot=self.bot)

        self.db.message_handler()(self.various_cmd_handler)

    async def various_cmd_handler(self, message: aiogram.types.Message):
        _LOGGER.info(
            get_log_cover("Get message"),
            message.text + '\n' + str(message.from_user)
        )
        if not message.text.startswith('/'):  # Not a command
            return

        main_command = message.text.split('_')[0][1:]

        if main_command in self.observer.active_clients:
            bot_message = TelegramBotCommand(message.text, message.from_user)
            result = await self.observer.handle_command(bot_message)
            await message.reply(result)
        elif main_command == "getAvailableMethods":
            bot_message = TelegramBotCommand(message.text, message.from_user)
            await self.observer.save_new_client(bot_message)
        else:
            result = await self.main_menu_handler(main_command)
            await message.reply(result)

    async def send_message(self, user_id, message):
        await self.bot.send_message(user_id, message)

    async def main_menu_handler(self, cmd):
        if cmd == "help":
            return self.main_menu

        return "main_kekos"

    @property
    def main_menu(self):
        menu = "\n".join(
            f"/{command.cmd} - {command.description}"
            for command in self.MAIN_MENU
        ) + "\n" + "\n".join(f"/{client}" for client in self.observer.active_clients.keys())
        return menu


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

    async def handle_command(self, message: TelegramBotCommand) -> str:
        print("handle: ", message.cmd)

        await self.bot.send_message(message.from_user.id, "GIGGITY")

        return "kekos"

    def new_sse_connection(self, client_name: str):
        client_queue = asyncio.Queue()
        self.active_clients[client_name] = client_queue
        return client_queue

    def stop_sse_connection(self, client_name: str):
        self.active_clients.pop(client_name)

    async def save_new_client(self, register_message: TelegramBotCommand):
        pass

    async def sent_event_to_client(self, client_name: str, event: SSEEvent):
        client_queue: asyncio.Queue = self.active_clients[client_name]
        await client_queue.put(event)

import asyncio
from functools import singledispatch
from typing import List

import aiogram
import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core._helpers import TargetTypes
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.config import config
from core.inbox.messages import BaseMessage, DocumentMessage, PhotoMessage
from core.sse.sse_event import SSEEvent
from core.sse.sse_server import create_sse_server
from core.inbox.consumer import RabbitConsumer, TelegramLeverMessage
# from core.bot import ControlBot
from core.memory_storage import MemoryStorage


_LOGGER = logging.getLogger(__name__)


#TODO singletone
class Observer:

    def __init__(self):
        self._rabbit_inbox = asyncio.Queue()

        self.rabbit = RabbitConsumer(
            **config["rabbit"],
            inbox_queue=self._rabbit_inbox,
        )
        self.sse_server = create_sse_server(self)
        # self.bot = ControlBot(self)
        self.memory_storage = MemoryStorage()

        self.d = d

        self.active_clients = dict()

    def run(self):
        self.d.observer = self

        asyncio.ensure_future(self.rabbit.listen_to_rabbit())
        asyncio.ensure_future(self.message_consumer())
        aiogram.executor.start_polling(self.d, skip_updates=True)

    async def message_consumer(self):
        while True:
            message: BaseMessage = await self._rabbit_inbox.get()
            self._rabbit_inbox.task_done()
            _LOGGER.info("Get message: %s", message)

            if message.cmd == 'getAvailableMethods':
                self.save_client_commands(message)
            else:
                # message_kwargs = message.get_params_to_sent()
                await send(message, bot=self.d.bot)

    def new_sse_connection(self, client_name: str):
        client_queue = asyncio.Queue()
        self.active_clients[client_name] = client_queue
        return client_queue

    def save_client_commands(self, message: TelegramLeverMessage):
        client_name = message.target.target_name

        assert message.target.target_type == TargetTypes.SERVICE.value
        assert client_name in self.active_clients

        self.memory_storage.save_client(client_name, message.commands)

    def get_command_info(self, client_name, command):
        return self.memory_storage.get_command_info(client_name, command)

    def get_client_info(self, client_name):
        return self.memory_storage.get_client_info(client_name)

    def stop_sse_connection(self, client_name: str):
        self.active_clients.pop(client_name)
        self.memory_storage.remove_client(client_name)

    async def emit_event(self, client_name: str, event: SSEEvent):
        try:
            client_queue: asyncio.Queue = self.active_clients[client_name]
            await client_queue.put(event)
        except KeyError:
            return "Unknown Client"

    async def send_message_to_user(self, **kwargs):
        return await self.d.bot.send_message(parse_mode='HTML', **kwargs)


@singledispatch
async def send(message, bot=None):
    ...


@send.register
async def _(message: DocumentMessage, bot=None):
    return await bot.send_document(parse_mode='HTML', **message.get_params_to_sent())


@send.register
async def _(message: TelegramLeverMessage, bot=None):
    return await bot.send_message(parse_mode='HTML', **message.get_params_to_sent())


@send.register
async def _(message: PhotoMessage, bot=None):
    return await bot.send_photo(parse_mode='HTMl', **message.get_params_to_sent())

    # async def send_message_to_user(self, message: TelegramLeverMessage):
    #     return await self.d.bot.send_message(parse_mode='HTML', **message.get_params_to_sent())
    #
    # async def send_document(self, document_message):
    #     return await self.d.bot.send_document(parse_mode='HTML', **document_message.get_params_to_sent())



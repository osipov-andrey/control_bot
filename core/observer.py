import asyncio
import aiogram
import logging

from functools import singledispatchmethod

from aiogram.utils import exceptions

from core._helpers import TargetTypes
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.config import config
from core.inbox.dispatcher import RabbitDispatcher
from core.inbox.messages import DocumentMessage, PhotoMessage, EditTextMessage, message_fabric
from core.sse.sse_event import SSEEvent
from core.sse.sse_server import create_sse_server
from core.inbox.consumer import RabbitConsumer, TextMessage
# from core.bot import ControlBot
from core.memory_storage import ControlBotMemoryStorage


_LOGGER = logging.getLogger(__name__)


#TODO singletone
class Observer:
    """ Класс связывающий различные компоненты программы """
    def __init__(self):
        self._rabbit_inbox = asyncio.Queue()

        self.rabbit = RabbitConsumer(**config["rabbit"], inbox_queue=self._rabbit_inbox)
        self.rabbit_dispatcher = RabbitDispatcher(self, self._rabbit_inbox)
        self.sse_server = create_sse_server(self)

        # self.bot = ControlBot(self)
        self.memory_storage = ControlBotMemoryStorage()

        self.d = d

        self.active_clients = dict()

    def run(self):
        self.d.observer = self

        asyncio.ensure_future(self.rabbit.listen_to_rabbit())
        asyncio.ensure_future(self.rabbit_dispatcher.message_dispatcher())
        aiogram.executor.start_polling(self.d, skip_updates=True)

    def new_sse_connection(self, client_name: str):
        client_queue = asyncio.Queue()
        self.active_clients[client_name] = client_queue
        return client_queue

    def save_client_info(self, message: TextMessage):
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

    async def send(self, message):
        try:
            return await self._send(message)
        except aiogram.utils.exceptions.MessageIsTooLong:
            message_params = {
                # TODO: заменить этот параметр на 'text', начиная с левера
                "message": "Message is too long!",
                "target": message.target
            }
            error_message = message_fabric(message_params)
            return await self._send(error_message)

    @singledispatchmethod
    async def _send(self, message):
        ...

    @_send.register
    async def _(self, message: DocumentMessage):
        return await self.d.bot.send_document(**message.get_params_to_sent())

    @_send.register
    async def _(self, message: TextMessage):
        return await self.d.bot.send_message(**message.get_params_to_sent())

    @_send.register
    async def _(self, message: PhotoMessage):
        return await self.d.bot.send_photo(**message.get_params_to_sent())

    @_send.register
    async def _(self, message: EditTextMessage):
        return await self.d.bot.edit_message_text(**message.get_params_to_sent())

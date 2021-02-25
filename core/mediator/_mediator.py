import asyncio
import logging
from functools import singledispatchmethod

import aiogram
from aiogram.utils import exceptions

from core.bot.telegram_api import telegram_api_dispatcher as d
from core.config import config
from core.inbox.consumers.rabbit import RabbitConsumer
from core.inbox.dispatcher import InboxDispatcher
from core.inbox.messages import BaseMessage, DocumentMessage, PhotoMessage, EditTextMessage, \
    TextMessage, message_fabric
from core.memory_storage import ControlBotMemoryStorage
from core.sse.sse_server import create_sse_server
from ._interfaces import *

_LOGGER = logging.getLogger(__name__)
_LOGGER.debug(config)


__all__ = ['Mediator']


class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Mediator(metaclass=SingletonMeta):
    """ Класс связывающий различные компоненты программы """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):

        memory_storage = ControlBotMemoryStorage()

        self.memory_storage = memory_storage

        self.users = UsersInterface()
        self.channels = ChannelsInterface()
        self.actuators = ActuatorsInterface(memory_storage)

        self.inbox_queue = asyncio.Queue()
        self.inbox_dispatcher = InboxDispatcher(self, self.inbox_queue)
        self.d = d

        self._rabbit = RabbitConsumer(**config["rabbit"], inbox_queue=self.inbox_queue)
        self._sse_server = create_sse_server(self)
        _LOGGER.debug("Mediator initialized!")
        print("Mediator initialized!")

    def run(self):
        # TODO разделить посредник и запускатор программы
        # Для доступа к интерфейсам из любой части программы:
        self.d.observer = self

        asyncio.ensure_future(self._rabbit.listen_to_rabbit())
        asyncio.ensure_future(self.inbox_dispatcher.message_dispatcher())
        aiogram.executor.start_polling(self.d, skip_updates=True)

    async def send(self, message: BaseMessage):
        """ Отправить сообщение в телеграм """
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


mediator = Mediator()
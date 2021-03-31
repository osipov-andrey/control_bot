import logging
from functools import singledispatchmethod

import aiogram
from aiogram.utils import exceptions

from core.config import config
from core.inbox.messages import (
    DocumentMessage,
    PhotoMessage,
    EditTextMessage,
    TextMessage,
    OutgoingMessage,
)
from core.ram_storage._memory_storage import ControlBotMemoryStorage
from core.sse.sse_server import create_sse_server
from ._interfaces import *


_LOGGER = logging.getLogger(__name__)
_LOGGER.debug(config)


__all__ = ["Mediator"]


class _SingletonMeta(type):

    _instances: dict = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Mediator(metaclass=_SingletonMeta):
    """ Класс связывающий различные компоненты программы """

    def __init__(self, telegram_api_dispatcher):

        memory_storage = ControlBotMemoryStorage()

        self.memory_storage = memory_storage

        self.users = UsersInterface()
        self.channels = ChannelsInterface()
        self.actuators = ActuatorsInterface(memory_storage)

        self.telegram_dispatcher = telegram_api_dispatcher

        self._sse_server = create_sse_server(self)
        _LOGGER.info("Mediator initialized!")

    async def send(self, message: OutgoingMessage):
        """ Отправить сообщение в телеграм """
        try:
            return await self._send(message)
        except aiogram.utils.exceptions.MessageIsTooLong:
            error_message = OutgoingMessage(
                chat_id=message.chat_id, text="Message is too long!"
            )
            return await self._send(error_message)

    @singledispatchmethod
    async def _send(self, message):
        ...

    @_send.register
    async def _send_document(self, message: DocumentMessage):
        return await self.telegram_dispatcher.bot.send_document(
            **message.get_params_to_sent()
        )

    @_send.register
    async def _send_text(self, message: TextMessage):
        return await self.telegram_dispatcher.bot.send_message(
            **message.get_params_to_sent()
        )

    @_send.register
    async def _send_photo(self, message: PhotoMessage):
        return await self.telegram_dispatcher.bot.send_photo(
            **message.get_params_to_sent()
        )

    @_send.register
    async def _edit_text(self, message: EditTextMessage):
        return await self.telegram_dispatcher.bot.edit_message_text(
            **message.get_params_to_sent()
        )

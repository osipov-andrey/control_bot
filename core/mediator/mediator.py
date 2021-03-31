import logging

import aiogram
from aiogram.utils import exceptions

from core.inbox.messages import OutgoingMessage
from core.ram_storage import ControlBotMemoryStorage
from ._interfaces import *


_LOGGER = logging.getLogger(__name__)

__all__ = ["Mediator"]


class _SingletonMeta(type):

    _instances: dict = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Mediator(metaclass=_SingletonMeta):
    """ Mediator between telegram API, repository, RAM-storage """

    def __init__(self, telegram_api_dispatcher=None):

        if not telegram_api_dispatcher:
            raise ValueError("Can't instantiate mediator without telegram_api_dispatcher!")

        memory_storage = ControlBotMemoryStorage()

        self.memory_storage = memory_storage
        self.telegram_dispatcher = telegram_api_dispatcher

        self.users = UsersInterface()
        self.channels = ChannelsInterface()
        self.actuators = ActuatorsInterface(memory_storage)

        _LOGGER.info("Mediator initialized!")

    async def send(self, message: OutgoingMessage):
        """ Send message to telegram API """
        try:
            return await self.telegram_dispatcher.send(message)
        except aiogram.utils.exceptions.MessageIsTooLong:
            error_message = OutgoingMessage(chat_id=message.chat_id, text="Message is too long!")
            return await self.telegram_dispatcher.send(error_message)

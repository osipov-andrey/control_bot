import asyncio
from abc import ABC
from typing import List

import aiogram
import logging

from functools import singledispatchmethod

from aiogram.utils import exceptions

from core._helpers import TargetTypes
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.config import config
from core.inbox.dispatcher import InboxDispatcher
from core.inbox.messages import BaseMessage, DocumentMessage, PhotoMessage, EditTextMessage, \
    TextMessage, message_fabric
from core.local_storage.exceptions import NoSuchUser
from core.local_storage.local_storage import Channel, LocalStorage, User
from core.sse.sse_event import SSEEvent
from core.sse.sse_server import create_sse_server
from core.inbox.consumers.rabbit import RabbitConsumer
from core.memory_storage import ControlBotMemoryStorage


_LOGGER = logging.getLogger(__name__)
_LOGGER.debug(config)


class BaseInterface(ABC):

    def __init__(self):

        self.db = LocalStorage()
        self.d = d


class ActuatorsInterface(BaseInterface):

    def __init__(self, memory_storage):
        super().__init__()
        self.memory_storage = memory_storage
        self.connected_actuators = dict()

    def is_connected(self, actuator_name) -> bool:
        return actuator_name in self.connected_actuators.keys()

    def save_actuator_info(self, message: TextMessage):
        """ Сохранить логику актуатора в ОЗУ """
        actuator_name = message.target.target_name

        assert message.target.target_type == TargetTypes.SERVICE.value
        assert actuator_name in self.connected_actuators

        self.memory_storage.save_client(actuator_name, message.commands)

    def get_command_info(self, actuator_name: str, command: str):
        """ Получить информацию о команде актуатора """
        return self.memory_storage.get_command_info(actuator_name, command)

    def get_actuator_info(self, actuator_name: str):
        """ Получить информацию о всех командах актуатора """
        return self.memory_storage.get_client_info(actuator_name)

    def new_sse_connection(self, actuator_name: str) -> asyncio.Queue:
        """ Подключить к интерфейсу новый актуатор  """
        actuator_queue = asyncio.Queue()
        self.connected_actuators[actuator_name] = actuator_queue
        return actuator_queue

    async def create_actuator(self, actuator_name: str, description: str):
        return await self.db.create_actuator(actuator_name, description)

    async def delete_actuator(self, actuator_name: str):
        return await self.db.delete_actuator(actuator_name)

    async def emit_event(self, actuator_name: str, event: SSEEvent):
        """ Отправить ЕVENT в актуатор """
        try:
            actuator_queue: asyncio.Queue = self.connected_actuators[actuator_name]
            await actuator_queue.put(event)
        except KeyError:
            return "Unknown Client"

    async def grant(self, telegram_id: int, actuator_name: str):
        """ Предоставить пользователю доступ к актуатору """
        return await self.db.grant(telegram_id, actuator_name)

    async def revoke(self, telegram_id: int, actuator_name: str):
        """ Забрать у пользователя доступ к актуатору """
        return await self.db.revoke(telegram_id, actuator_name)

    async def get_all(self):
        """ Получить все зарегистрированные актуаторы """
        actuators = await self.db.get_actuators()
        return actuators

    async def get_granters(self, actuator_name: str):
        """ Получить пользователей с доступом к актуатору """
        granters = await self.db.get_granters(actuator_name)
        return granters

    def stop_sse_connection(self, actuator_name: str):
        """ Подключить актуатор от интерфейса """
        self.connected_actuators.pop(actuator_name)
        self.memory_storage.remove_client(actuator_name)


class ChannelsInterface(BaseInterface):

    async def all_channels(self) -> List[Channel]:
        return await self.db.all_channels()

    async def create_channel(self, channel: str, description: str) -> bool:
        return await self.db.save_channel(channel, description)

    async def delete_channel(self, channel: str) -> bool:
        return await self.db.delete_channel(channel)

    async def subscribe(self, user_telegram_id: int, channel: str):
        await self.db.channel_subscribe(user_telegram_id, channel)

    async def unsubscribe(self, user_telegram_id: int, channel: str):
        await self.db.channel_unsubscribe(user_telegram_id, channel)

    async def get_subscribers(self, channel: str) -> List[User]:
        subscribers = await self.db.get_subscribers(channel)
        return subscribers


class UsersInterface(BaseInterface):

    async def upsert(
            self,
            **kwargs
    ):
        return await self.db.upsert_user(**kwargs)

    async def get_admins(self) -> List[User]:
        return await self.db.get_admins()

    async def is_admin(self, telegram_id: int) -> bool:
        """ Проверка админских прав у пользователя """
        try:
            user: User = await self.db.get_user(telegram_id)
        except NoSuchUser:
            return False
        return bool(user.is_admin)

    async def get_all(self) -> List[User]:
        """ Получить ВСЕХ пользователей """
        users = await self.db.get_all_users()
        return users

    async def subscribes(self, telegram_id: int) -> List[Channel]:
        """ Получить подписки пользователя """
        subs = await self.db.get_user_subscribes(telegram_id)
        return subs

    async def has_grant(self, telegram_id: int, actuator_name: str) -> bool:
        """ Есть ли у пользователя доступ к актутатору """
        result = await self.db.user_has_grant(telegram_id, actuator_name)
        return result


#TODO singletone
class Mediator:
    """ Класс связывающий различные компоненты программы """

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

import asyncio
from typing import Protocol, Any, List

from core.inbox.models import Issue, ActuatorMessage, CommandSchema
from core.repository import User, Channel, Actuator
from core.sse.sse_event import SSEEvent


class MediatorProto(Protocol):
    memory_storage: 'ControlBotMemoryStorageProto'
    telegram_dispatcher: Any  # TODO: dispatcher
    users: 'UsersInterfaceProto'
    channels: 'ChannelsInterfaceProto'
    actuators: 'ActuatorsInterfaceProto'

    async def send(self, message) -> Any:  # TODO: from dispatcher
        ...


class ControlBotMemoryStorageProto(Protocol):

    def save_actuator_info(self, actuator_name: str, commands_info: dict) -> None:
        ...

    def remove_actuator(self, actuator_name: str) -> None:
        ...

    def get_actuator_info(self, actuator_name: str) -> dict:
        """
        Raises NoSuchActuatorInRAM if actuator was not found
        :param actuator_name:
        :return:
        """
        ...

    def get_command_info(self, actuator_name: str, command: str) -> dict:
        """
        Raises NoSuchCommand if command was not found for actuator
        :param command:
        :param actuator_name:
        :return:
        """
        ...

    def set_issue(self, issue: Issue) -> None:
        ...

    def resolve_issue(self, issue_id: str) -> Issue:
        ...


class UsersInterfaceProto(Protocol):

    async def upsert(self, **kwargs) -> User:
        ...

    async def get_admins(self) -> List[User]:
        ...

    async def is_admin(self, telegram_id: int) -> bool:
        """
        Проверка админских прав у пользователя
        Raises NoSuchUser if user was not found
        """
        ...

    async def get_all(self) -> List[User]:
        """Получить ВСЕХ пользователей"""
        ...

    async def subscribes(self, telegram_id: int) -> List[Channel]:
        """Получить подписки пользователя"""
        ...

    async def has_grant(self, telegram_id: int, actuator_name: str) -> bool:
        """Есть ли у пользователя доступ к актутатору"""
        ...


class ChannelsInterfaceProto(Protocol):

    async def all_channels(self) -> List[Channel]:
        ...

    async def create_channel(self, channel: str, description: str) -> bool:
        ...

    async def delete_channel(self, channel: str) -> bool:
        ...

    async def subscribe(self, user_telegram_id: int, channel: str):
        ...

    async def unsubscribe(self, user_telegram_id: int, channel: str):
        ...

    async def get_subscribers(self, channel: str) -> List[User]:
        ...

    async def get_subscribes(self, user_telegram_id: int) -> List[Channel]:
        ...


class ActuatorsInterfaceProto(Protocol):

    def is_connected(self, actuator_name) -> bool:
        ...

    def save_actuator_info(self, message: ActuatorMessage):
        """Сохранить логику актуатора в ОЗУ"""
        ...

    def get_command_info(self, actuator_name: str, command: str) -> CommandSchema:
        """Получить информацию о команде актуатора"""
        ...

    def get_actuator_info(self, actuator_name: str) -> dict:
        """Получить информацию о всех командах актуатора"""
        ...

    async def create_actuator(self, actuator_name: str, description: str) -> bool:
        ...

    async def delete_actuator(self, actuator_name: str) -> bool:
        ...

    async def emit_event(self, actuator_name: str, event: SSEEvent) -> None:
        """Отправить ЕVENT в актуатор"""
        ...

    async def grant(self, telegram_id: int, actuator_name: str) -> bool:
        """Предоставить пользователю доступ к актуатору"""
        ...

    async def revoke(self, telegram_id: int, actuator_name: str) -> bool:
        """Забрать у пользователя доступ к актуатору"""
        ...

    async def get_all(self) -> List[Actuator]:
        """Получить все зарегистрированные актуаторы"""
        ...

    async def get_granters(self, actuator_name: str) -> List[User]:
        """Получить пользователей с доступом к актуатору"""
        ...

    async def turn_on_actuator(self, actuator_name: str) -> asyncio.Queue:
        """
        Turn on the actuator
        Raises ActuatorAlreadyConnected
        """
        ...

    async def turn_off_actuator(self, actuator_name: str) -> None:
        """Turn off the actuator"""
        ...

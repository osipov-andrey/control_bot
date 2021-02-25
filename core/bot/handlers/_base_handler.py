from abc import abstractmethod, ABC

from aiogram import types
from aiogram.dispatcher import FSMContext


class MessageHandler(ABC):

    def __init__(self):

        self.user_telegram_id = None
        self.is_admin = None

    @property
    def mediator(self):
        from mediator import mediator
        return mediator

    async def callback(self, message: types.Message, state: FSMContext, **kwargs):
        self.user_telegram_id = message.from_user.id
        self.is_admin = await self.mediator.users.is_admin(self.user_telegram_id)
        await self.execute(message, state, **kwargs)

    @abstractmethod
    async def execute(self, message: types.Message, state: FSMContext, **kwargs):
        ...

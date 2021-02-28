from abc import abstractmethod, ABC
from dataclasses import asdict
from typing import Optional

from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget, TargetType


class MessageHandler(ABC):

    def __init__(self):

        self.user_telegram_id = None
        self.is_admin = None
        self.kwargs_to_answer: Optional[dict] = None

    @property
    def mediator(self):
        from mediator import mediator
        return mediator

    async def callback(self, message: types.Message, state: FSMContext, **kwargs):
        self.user_telegram_id = message.from_user.id
        self.is_admin = await self.mediator.users.is_admin(self.user_telegram_id)
        self.kwargs_to_answer = {
            # kwargs for sending a message to the user
            "target": asdict(MessageTarget(TargetType.USER.value, self.user_telegram_id))
        }
        await self.handle(message, state, **kwargs)

    @abstractmethod
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        ...

    @staticmethod
    async def _answer(message, text):
        await message.answer(text, parse_mode="HTML")

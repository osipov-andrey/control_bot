from abc import abstractmethod, ABC
from typing import Optional, Union

from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._notification_constants import CONTEXT_CANCEL_MENU
from core.mediator.dependency import MediatorDependency


class MessageHandler(ABC, MediatorDependency):
    """ Custom class-based handler for use with aiogram """

    def __init__(self):
        self.user_telegram_id = None
        self.is_admin = None
        self.kwargs_to_answer: Optional[dict] = None

    async def callback(
        self,
        message: Union[types.Message, types.CallbackQuery],
        state: FSMContext,
        **kwargs,
    ):
        """ Callback for use in `core.bot.telegram_api.CustomDispatcher` """
        self.user_telegram_id = message.from_user.id
        self.is_admin = await self.mediator.users.is_admin(self.user_telegram_id)
        self.kwargs_to_answer = {
            # kwargs for sending a message to the user
            "chat_id": self.user_telegram_id
        }
        await self.handle(message, state, **kwargs)

    @abstractmethod
    async def handle(
        self,
        message: Union[types.Message, types.CallbackQuery],
        state: FSMContext,
        **kwargs,
    ):
        """ Place for handling logic """
        ...

    @staticmethod
    async def _answer(message, text):
        text += f"\n{CONTEXT_CANCEL_MENU}"
        await message.answer(text, parse_mode="HTML")

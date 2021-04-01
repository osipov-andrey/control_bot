from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot.telegram_api import telegram_api_dispatcher


@telegram_api_dispatcher.message_handler(commands=["cancel"], state="*")
async def cancel(message: types.Message, state: FSMContext):
    """ Reset current state """
    if (
        await state.storage.get_state(
            user=message["from"]["id"], chat=message["chat"]["id"]
        )
        is not None
    ):
        await state.reset_state()
        await message.answer(
            "Action canceled!", reply_markup=types.ReplyKeyboardRemove()
        )

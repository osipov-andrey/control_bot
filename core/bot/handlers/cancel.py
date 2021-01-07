from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot.telegram_api import telegram_api_dispatcher as d


@d.message_handler(commands=["cancel"], state="*")
async def cancel(message: types.Message, state: FSMContext):
    if await state.storage.get_state(
            user=message["from"]["id"],
            chat=message["chat"]["id"]
    ) is not None:
        await message.answer("Действие отменено!", reply_markup=types.ReplyKeyboardRemove())
        await state.reset_state()

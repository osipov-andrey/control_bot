from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._helpers import get_menu, MenuTextButton
from core.bot.states import MainMenu
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.local_storage.db_enums import UserEvents
from core.local_storage.local_storage import LocalStorage


@d.message_handler(commands=["me"])
async def users_handler(message: types.Message):
    await MainMenu.me.set()
    menu = get_menu(
        header="Список команд: ",
        commands=[
            MenuTextButton("introduce", "записать ваш telegram ID в бот"),
        ]
    )
    await message.answer(menu)


@d.message_handler(commands=["introduce"], state=MainMenu.me)
async def introduce_handler(message: types.Message, state: FSMContext):
    db: LocalStorage = d.observer.db
    user_status = await db.upsert_user(
        tg_id=message.from_user.id,
        tg_username=message.from_user.username,
        name=message.from_user.full_name,
    )

    if user_status == UserEvents.CREATED:
        await message.answer("Вы зарегистрировались в боте")
    elif user_status == UserEvents.UPDATED:
        await message.answer("Ваши данные обновлены")
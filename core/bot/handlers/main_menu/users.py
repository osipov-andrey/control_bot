from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._helpers import get_menu, MenuTextButton
from core.bot.states import MainMenu
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.local_storage.db_enums import UserEvents
from core.local_storage.local_storage import LocalStorage


@d.message_handler(commands=["users"])
async def users_handler(message: types.Message):
    await MainMenu.users.set()
    menu = get_menu(
        header="Список команд: ",
        commands=[
                     MenuTextButton("all_users", "Список пользователей"),
                 ]
    )
    await message.answer(menu)


@d.message_handler(commands=["all_users"], state=MainMenu.users)
async def all_users_handler(message: types.Message, state: FSMContext):
    db: LocalStorage = d.observer.db
    users = await db.get_all_users()
    await message.answer(users)


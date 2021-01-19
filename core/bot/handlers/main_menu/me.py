from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._helpers import get_menu, MenuTextButton
from core.bot.states import MainMenu
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.local_storage.db_enums import UserEvents


@d.message_handler(commands=["me"])
async def users_handler(message: types.Message):
    await MainMenu.me.set()
    menu = get_menu(
        header="Список команд: ",
        commands=[
            MenuTextButton("introduce", "записать ваш telegram ID в бот"),
            MenuTextButton("myID", "узнать ваш telegram ID в бот"),
            MenuTextButton("myChannels", "мои каналы"),
        ]
    )
    await message.answer(menu)


@d.message_handler(commands=["introduce"], state=MainMenu.me)
async def introduce_handler(message: types.Message, state: FSMContext):
    observer = d.observer
    user_status = await observer.users.upsert(
        tg_id=message.from_user.id,
        tg_username=message.from_user.username,
        name=message.from_user.full_name,
    )

    if user_status == UserEvents.CREATED:
        await message.answer("Вы зарегистрировались в боте")
    elif user_status == UserEvents.UPDATED:
        await message.answer("Ваши данные обновлены")

    await state.reset_state()


@d.message_handler(commands=["myID"], state=MainMenu.me)
async def introduce_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer(f"Ваш telegram ID: {user_id}")
    await state.reset_state()


@d.message_handler(commands=["myChannels"], state=MainMenu.me)
async def my_channels_handler(message: types.Message, state: FSMContext):
    print("channels")


@d.message_handler(commands=["unsubscribe"], state=MainMenu.me)
async def unsubscribe_handler(message: types.Message, state: FSMContext):
    ...
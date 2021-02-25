from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._helpers import get_menu, MenuTextButton
from core.bot.states import MainMenu
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.repository._db_enums import UserEvents
from core.bot.handlers._static_commands import *


@d.message_handler(commands=[ME])
async def users_handler(message: types.Message):
    await MainMenu.me.set()
    menu = get_menu(
        header="Account settings: ",
        commands=[
            MenuTextButton(INTRODUCE, "Write my ID to the bot"),
            MenuTextButton(MY_ID, "My telegram ID"),
            MenuTextButton(MY_CHANNELS, "My channels"),
        ]
    )
    await message.answer(menu)


@d.message_handler(commands=[INTRODUCE], state=MainMenu.me)
async def introduce_handler(message: types.Message, state: FSMContext):
    from mediator import mediator
    user_status = await mediator.users.upsert(
        tg_id=message.from_user.id,
        tg_username=message.from_user.username,
        name=message.from_user.full_name,
    )

    if user_status == UserEvents.CREATED:
        await message.answer("You have registered")
    elif user_status == UserEvents.UPDATED:
        await message.answer("Your contact information has been updated")

    await state.reset_state()


@d.message_handler(commands=[MY_ID], state=MainMenu.me)
async def introduce_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer(f"Your telegram ID: {user_id}")
    await state.reset_state()


@d.message_handler(commands=[MY_CHANNELS], state=MainMenu.me)
async def my_channels_handler(message: types.Message, state: FSMContext):
    print("channels")


@d.message_handler(commands=[UNSUBSCRIBE], state=[MainMenu.me, MainMenu.channels])
async def unsubscribe_handler(message: types.Message, state: FSMContext):
    ...
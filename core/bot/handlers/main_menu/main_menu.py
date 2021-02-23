from aiogram import types

from core.bot._helpers import get_menu, MenuTextButton
from core.bot.telegram_api import telegram_api_dispatcher
from core.bot.handlers._static_commands import *


@telegram_api_dispatcher.message_handler(commands=[START])
async def main_menu_handler(message: types.Message, state):
    observer = telegram_api_dispatcher.observer
    telegram_id = message.from_user.id
    is_admin = await observer.users.is_admin(telegram_id)
    admins = await observer.users.get_admins()
    if not admins:
        await _auto_create_admin(observer, message)
        return

    actuators = [
        MenuTextButton(actuator.name, actuator.description)
        for actuator in await observer.actuators.get_all()
        if observer.actuators.is_connected(actuator.name)
        and await observer.users.has_grant(telegram_id, actuator.name)
    ]
    menu = get_menu(
        header="Main menu:",
        commands=[
            MenuTextButton(START, "main menu"),
            MenuTextButton(USERS, "actions with users", admin_only=True),
            MenuTextButton(CHANNELS, "actions with channels", admin_only=True),
            MenuTextButton(ACTUATORS, "actions with actuators", admin_only=True),
            MenuTextButton(ME, "account settings"),
        ] + actuators,
        is_admin=is_admin
    )
    await message.answer(menu)


async def _auto_create_admin(observer, message: types.Message):
    await observer.users.upsert(
        tg_id=message.from_user.id,
        tg_username=message.from_user.username,
        name=message.from_user.full_name,
        is_admin=True
    )
    await message.answer("You are now the bot administrator")

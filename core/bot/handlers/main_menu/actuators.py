from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget, TargetTypes
from core.bot._helpers import admin_only, delete_cmd_prefix, get_menu, MenuTextButton
from core.bot.handlers._static_commands import *
from core.bot.handlers.main_menu.users_commands import get_grant_or_revoke_cmd, \
    get_subscribe_or_unsubscribe_cmd, get_create_or_delete_cmd
from core.bot.states import MainMenu
from core.bot.state_enums import CommandFillStatus
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.local_storage.exceptions import AlreadyHasItException, NoSuchUser
from core.local_storage.local_storage import LocalStorage
from core.bot.handlers.main_menu._workflow import start_cmd_internal_workflow


@d.message_handler(commands=["actuators"])
@admin_only
async def actuators_handler(message: types.Message, state: FSMContext):
    await MainMenu.actuators.set()
    menu = get_menu(
        header="Список команд: ",
        commands=[
            MenuTextButton("all_actuators", "-------"),
            MenuTextButton("create", "Create actuator"),
            MenuTextButton("delete", "Delete actuator"),
            MenuTextButton("grant", "Предоставить пользователю доступ к актуатору"),
            MenuTextButton("revoke", "Закрыть пользователю доступ к актуатору"),
            # grant, revoke - calling from users submenu
        ]
    )
    await message.answer(menu)


@d.message_handler(commands=[CREATE_ACTUATOR, DELETE_ACTUATOR], state=MainMenu.actuators)
async def create_delete_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    is_admin = True  # в state=MainMenu.actuators может попасть только админ
    cmd_text = delete_cmd_prefix(message.text)
    cmd = get_create_or_delete_cmd(cmd_text, user_id, is_admin)

    message_kwargs = {
        "target": MessageTarget(TargetTypes.USER.value, user_id)._asdict()
    }

    async def create_callback(**kwargs):
        actuator_name = kwargs.get("actuator_name")
        description = kwargs.get("description")
        await d.observer.actuators.create_actuator(actuator_name, description)
        await message.answer(f"Создан актуатор {actuator_name} - {description}.")

    async def delete_callback(**kwargs):
        actuator_name = kwargs.get("actuator_name")
        await d.observer.actuators.delete_actuator(actuator_name)
        await message.answer(f"Удален актуатор {actuator_name}.")

    if cmd_text == CREATE_ACTUATOR:
        callback = create_callback
    elif cmd_text == DELETE_ACTUATOR:
        callback = delete_callback
    else:
        await message.answer(text="Неизвестная команда")
        return
    await start_cmd_internal_workflow(
        state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, callback=callback
    )

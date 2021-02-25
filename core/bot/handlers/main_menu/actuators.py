from dataclasses import asdict

from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget, TargetType
from core.bot._helpers import admin_only_func, delete_cmd_prefix, get_menu, MenuTextButton
from core.bot.handlers._static_commands import *
from core.bot.handlers.main_menu.users_commands import get_create_or_delete_cmd
from core.bot.states import MainMenu
from core.bot.state_enums import CommandFillStatus
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.bot.handlers.main_menu._workflow import start_cmd_internal_workflow


@d.message_handler(commands=[ACTUATORS])
@admin_only_func
async def actuators_handler(message: types.Message, state: FSMContext):
    await MainMenu.actuators.set()
    menu = get_menu(
        header="Actuators menu: ",
        commands=[
            MenuTextButton(ALL_ACTUATORS, "-------"),
            MenuTextButton(CREATE_ACTUATOR, "Create actuator"),
            MenuTextButton(DELETE_ACTUATOR, "Delete actuator"),
            MenuTextButton(GRANT, "Предоставить пользователю доступ к актуатору"),
            MenuTextButton(REVOKE, "Закрыть пользователю доступ к актуатору"),
            # grant, revoke - calling from users submenu
        ]
    )
    await message.answer(menu)


@d.message_handler(commands=[CREATE_ACTUATOR, DELETE_ACTUATOR], state=MainMenu.actuators)
async def create_delete_handler(message: types.Message, state: FSMContext):
    from mediator import mediator
    user_id = message.chat.id
    is_admin = True  # в state=MainMenu.actuators может попасть только админ
    cmd_text = delete_cmd_prefix(message.text)
    cmd = get_create_or_delete_cmd(cmd_text, user_id, is_admin)

    message_kwargs = {
        "target": asdict(MessageTarget(TargetType.USER.value, user_id))
    }

    async def create_callback(**kwargs):
        actuator_name = kwargs.get("actuator")
        description = kwargs.get("description")
        await mediator.actuators.create_actuator(actuator_name, description)
        await message.answer(f"Создан актуатор {actuator_name} - {description}.")

    async def delete_callback(**kwargs):
        actuator_name = kwargs.get("actuator")
        await mediator.actuators.delete_actuator(actuator_name)
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

from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget, TargetTypes
from core.bot._helpers import admin_only, delete_cmd_prefix, get_menu, MenuTextButton
from core.bot.handlers.main_menu.users_commands import get_grant_or_revoke_cmd, \
    get_subscribe_or_unsubscribe_cmd
from core.bot.states import MainMenu
from core.bot.state_enums import CommandFillStatus
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.local_storage.local_storage import LocalStorage
from core.bot.handlers.main_menu._workflow import start_cmd_internal_workflow


@d.message_handler(commands=["users"])
@admin_only
async def users_handler(message: types.Message, state=MainMenu.users):
    await MainMenu.users.set()
    menu = get_menu(
        header="Список команд: ",
        commands=[
                     MenuTextButton("all_users", "Список пользователей"),
                     MenuTextButton("subscribe", "Подписать пользователя на канал"),
                     MenuTextButton("unsubscribe", "Отписать пользователя от канала"),
                     MenuTextButton("grant", "Предоставить пользователю доступ к актуатору"),
                     MenuTextButton("revoke", "Закрыть пользователю доступ к актуатору"),
                 ]
    )
    await message.answer(menu)


@d.message_handler(commands=["all_users"], state=MainMenu.users)
async def all_users_handler(message: types.Message, state: FSMContext):
    users = await d.observer.users.get_all()
    await message.answer(users)


@d.message_handler(commands=["subscribe", "unsubscribe"], state=MainMenu.users)
async def subscribe_handler(message: types.Message, state: FSMContext):

    user_id = message.chat.id
    is_admin = True  # в state=MainMenu.users может попасть только админ
    cmd_text = delete_cmd_prefix(message.text)
    cmd = get_subscribe_or_unsubscribe_cmd(cmd_text, user_id, is_admin)

    message_kwargs = {
        "target": MessageTarget(TargetTypes.USER.value, user_id)._asdict()
    }

    async def subscribe_callback(**kwargs):
        user_to_subs_id = kwargs.get("user_id")
        channel = kwargs.get("channel")
        await d.observer.channels.subscribe(user_to_subs_id, channel)
        await message.answer(f"Пользователь {user_to_subs_id} подписан на канал {channel}")

    async def unsubscribe_callback(**kwargs):
        user_to_subs_id = kwargs.get("user_id")
        channel = kwargs.get("channel")
        await d.observer.channels.unsubscribe(user_to_subs_id, channel)
        await message.answer(f"Пользователь {user_to_subs_id} отписан от канала {channel}")

    if cmd_text == "subscribe":
        callback = subscribe_callback
    elif cmd_text == "unsubscribe":
        callback = unsubscribe_callback
    else:
        await message.answer(text="Неизвестная команда")
        return
    await start_cmd_internal_workflow(
        state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, callback=callback
    )


@d.message_handler(commands=["grant", "revoke"], state=MainMenu.users)
async def grant_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    is_admin = True  # в state=MainMenu.users может попасть только админ
    cmd_text = delete_cmd_prefix(message.text)
    cmd = get_grant_or_revoke_cmd(cmd_text, user_id, is_admin)

    message_kwargs = {
        "target": MessageTarget(TargetTypes.USER.value, user_id)._asdict()
    }

    async def grant_callback(**kwargs):
        user_to_grant_id = kwargs.get("user_id")
        actuator = kwargs.get("actuator")
        await d.observer.actuators.grant(user_to_grant_id, actuator)
        await message.answer(f"Пользователю {user_to_grant_id} открыт доступ к {actuator}")

    async def revoke_callback(**kwargs):
        user_to_revoke_id = kwargs.get("user_id")
        actuator = kwargs.get("channel")
        await d.observer.actuators.revoke(user_to_revoke_id, actuator)
        await message.answer(f"Пользователю {user_to_revoke_id} закрыт доступ к {actuator}")

    if cmd_text == "grant":
        callback = grant_callback
    elif cmd_text == "unsubscribe":
        callback = revoke_callback
    else:
        await message.answer(text="Неизвестная команда")
        return
    await start_cmd_internal_workflow(
        state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, callback=callback
    )

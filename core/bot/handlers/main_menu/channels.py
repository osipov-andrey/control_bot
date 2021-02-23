from dataclasses import asdict

from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget, TargetType
from core.bot._helpers import admin_only, delete_cmd_prefix, get_menu, MenuTextButton
from core.bot.handlers._static_commands import *
from core.bot.handlers.main_menu.users_commands import get_create_or_delete_channel_cmd
from core.bot.states import MainMenu
from core.bot.state_enums import CommandFillStatus
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.bot.handlers.main_menu._workflow import start_cmd_internal_workflow


@d.message_handler(commands=[CHANNELS])
@admin_only
async def actuators_handler(message: types.Message, state: FSMContext):
    await MainMenu.channels.set()
    menu = get_menu(
        header="Channels menu: ",
        commands=[
            MenuTextButton(ALL_CHANNELS, "All channels"),
            MenuTextButton(CREATE_CHANNEL, "Create channel"),
            MenuTextButton(DELETE_CHANNEL, "Delete channel"),
            MenuTextButton(SUBSCRIBE, "Subscribe user to channel"),
            MenuTextButton(UNSUBSCRIBE, "Unsubscribe user from channel"),
            # subscribe, unsubscribe - calling from users submenu
        ]
    )
    await message.answer(menu)


@d.message_handler(commands=[CREATE_CHANNEL, DELETE_CHANNEL], state=MainMenu.channels)
async def create_delete_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    is_admin = True  # в state=MainMenu.channels может попасть только админ
    cmd_text = delete_cmd_prefix(message.text)
    cmd = get_create_or_delete_channel_cmd(cmd_text, user_id, is_admin)

    message_kwargs = {
        "target": asdict(MessageTarget(TargetType.USER.value, user_id))
    }

    async def create_callback(**kwargs):
        channel_name = kwargs.get("channel")
        description = kwargs.get("description")
        result = await d.observer.channels.create_channel(channel_name, description)
        # TODO: check result
        await message.answer(f"Channel created: {channel_name} - {description}.")

    async def delete_callback(**kwargs):
        channel_name = kwargs.get("channel")
        result = await d.observer.channels.delete_channel(channel_name)
        await message.answer(f"Channel deleted: {channel_name}.")

    if cmd_text == CREATE_CHANNEL:
        callback = create_callback
    elif cmd_text == DELETE_CHANNEL:
        callback = delete_callback
    else:
        await message.answer(text="Unknown command!")
        return
    await start_cmd_internal_workflow(
        state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, callback=callback
    )


@d.message_handler(commands=[ALL_CHANNELS], state=MainMenu.channels)
async def all_channels_handler(message: types.Message, state: FSMContext):
    answer = "<b>All channels:</b>\n"
    channels = await d.observer.channels.all_channels()
    if channels:
        answer += "\n".join(f"{channel.name} - {channel.description}" for channel in channels)
    else:
        answer += "\nNo channels"
    await message.answer(text=answer, parse_mode="HTML")

from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._helpers import get_menu, MenuTextButton, admin_only_method
from core.bot import emojies
from core.bot.handlers._base_handler import MessageHandler
from core.bot._command_constants import CHANNELS, ALL_CHANNELS, CREATE_CHANNEL, DELETE_CHANNEL, SUBSCRIBE, UNSUBSCRIBE
from core.bot.commands.internal.internal_commands_schemas import get_create_or_delete_channel_cmd
from core.bot.commands.internal.internal_commands_workflow import start_cmd_internal_workflow
from core.bot.states import MainMenu
from core.bot.state_enums import CommandFillStatus
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.bot._notification_templates import generate_channel_report


@d.class_message_handler(commands=[CHANNELS])
class ChannelsHandler(MessageHandler):
    """ Actuators submenu """
    @admin_only_method
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        await MainMenu.channels.set()
        menu = get_menu(
            header=f"{emojies.CHANNEL} Channels menu: ",
            commands=[
                MenuTextButton(ALL_CHANNELS, "All channels"),
                MenuTextButton(CREATE_CHANNEL, "Create channel"),
                MenuTextButton(DELETE_CHANNEL, "Delete channel"),
                MenuTextButton(SUBSCRIBE, "Subscribe user to channel"),
                MenuTextButton(UNSUBSCRIBE, "Unsubscribe user from channel"),
                # subscribe, unsubscribe - calling from users submenu
            ]
        )
        await self._answer(message, menu)


@d.class_message_handler(commands=[ALL_CHANNELS], state=MainMenu.channels)
class AllChannelsHandler(MessageHandler):
    """ Show all channels """
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        channels = await self.mediator.channels.all_channels()
        text = "<b>All channels:</b>\n" + generate_channel_report(channels)
        await self._answer(message, text)
        await state.reset_state()


@d.class_message_handler(commands=[CREATE_CHANNEL], state=MainMenu.channels)
class CreateChannelHandler(MessageHandler):
    """ Create channel """
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = get_create_or_delete_channel_cmd(CREATE_CHANNEL, self.user_telegram_id, self.is_admin)

        async def create_callback(**kwargs_):
            channel_name = kwargs_.get("channel")
            description = kwargs_.get("description")
            result = await self.mediator.channels.create_channel(channel_name, description)
            if result:
                text = f"Channel created: {channel_name} - {description}."
            else:
                text = f"Channel NOT created: {channel_name} - {description}!"
            await self._answer(message, text)

        await start_cmd_internal_workflow(
            state, cmd, self.kwargs_to_answer, CommandFillStatus.FILL_COMMAND, callback=create_callback
        )


@d.class_message_handler(commands=[DELETE_CHANNEL], state=MainMenu.channels)
class DeleteChannelHandler(MessageHandler):
    """ Delete channel """
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = get_create_or_delete_channel_cmd(DELETE_CHANNEL, self.user_telegram_id, self.is_admin)

        async def delete_callback(**kwargs_):
            channel_name = kwargs_.get("channel")
            result = await self.mediator.channels.delete_channel(channel_name)
            await message.answer(f"Channel deleted: {channel_name}.")

        await start_cmd_internal_workflow(
            state, cmd, self.kwargs_to_answer, CommandFillStatus.FILL_COMMAND, callback=delete_callback
        )

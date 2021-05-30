from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._helpers import delete_cmd_prefix
from core.bot.state_enums import CommandFillStatus
from core.bot.commands.internal.internal_command import InternalCommand
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.bot.commands.internal.internal_commands_workflow import (
    start_cmd_internal_workflow,
)
from core.bot.states import Command


@d.message_handler(state=Command.argument_internal)
async def argument_handler(message: types.Message, state: FSMContext):  # TODO: class-based
    """Handling Command Argument Input"""
    message_kwargs = {"chat_id": message.chat.id}
    data = await state.get_data()
    cmd: InternalCommand = data.get("cmd")
    argument_value = delete_cmd_prefix(message.text)
    cmd.fill_argument(argument_value)
    state_data = await state.get_data()
    callback = state_data.get("callback")
    await start_cmd_internal_workflow(
        state, cmd, message_kwargs, CommandFillStatus.FILL_ARGUMENTS, callback
    )

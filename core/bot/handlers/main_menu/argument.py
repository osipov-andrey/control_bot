from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget, TargetTypes
from core.bot.state_enums import CommandFillStatus
from core.bot.handlers.actuator_commands._command import InternalCommand
from core.bot.telegram_api import state_storage, telegram_api_dispatcher as d
from core.bot.handlers.main_menu._workflow import start_cmd_internal_workflow
from core.bot.states import Command


@d.message_handler(state=Command.argument_internal)
async def argument_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    message_kwargs = {"target": MessageTarget(TargetTypes.USER.value, user_id)._asdict()}
    data = await state.get_data()
    cmd: InternalCommand = data.get("cmd")

    argument_value = message.text
    cmd.fill_argument(argument_value)
    state_data = await state.get_data()
    callback = state_data.get("callback")
    await start_cmd_internal_workflow(state, cmd, message_kwargs, CommandFillStatus.FILL_ARGUMENTS, callback)

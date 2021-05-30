""" Actuator commands handlers """
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot.handlers._base_handler import MessageHandler
from core.bot.commands.actuator.actuator_command import ActuatorCommand
from core.bot.commands.actuator.actuator_commands_workflow import (
    start_actuator_command_workflow,
    continue_cmd_workflow,
)
from core.bot.state_enums import CommandFillStatus
from core.bot.states import Command
from core.bot.telegram_api import telegram_api_dispatcher as d


_COMMAND_REGEX = r"^\/([^_]*)_?.*?$"


@d.class_message_handler(regexp=_COMMAND_REGEX)
@d.class_message_handler(state=Command.client)
class ActuatorCommandHandler(MessageHandler):
    """Handle actuator command"""

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        await start_actuator_command_workflow(message, state, self.mediator)


@d.class_message_handler(state=Command.arguments)
class FillingArgumentHandler(MessageHandler):
    """Fill in the argument of the actuator command"""

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        data = await state.get_data()
        cmd: ActuatorCommand = data.get("cmd")
        argument_value = message.text
        cmd.fill_argument(argument_value)
        await continue_cmd_workflow(
            state,
            cmd,
            self.kwargs_to_answer,
            CommandFillStatus.FILL_ARGUMENTS,
            self.mediator,
        )


@d.class_callback_query_handler(state="*")
class InlineButtonHandler(MessageHandler):
    """Handling an inline button click"""

    async def handle(
        self, callback_query: Union[types.Message, types.CallbackQuery], state: FSMContext, **kwargs
    ):  # type: ignore
        await callback_query.answer("Button has been Pressed")
        message = callback_query.message
        message.text = callback_query.data
        await start_actuator_command_workflow(message, state, self.mediator, message.message_id)

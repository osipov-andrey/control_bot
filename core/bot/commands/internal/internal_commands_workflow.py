from typing import Callable, Optional

from aiogram.dispatcher import FSMContext

from core.bot._notification_constants import UNKNOWN_USER
from core.bot.state_enums import ArgumentsFillStatus
from core.bot.states import Command
from core.bot.commands.internal.internal_command import InternalCommand
from core.bot.telegram_api import state_storage
from core.inbox.messages import message_fabric
from core.repository.exceptions import NoSuchUser
from core.mediator.dependency import MediatorDependency


async def start_cmd_internal_workflow(
    state: FSMContext,
    cmd: InternalCommand,
    message_kwargs,
    fill_status,
    callback: Optional[Callable],
    message_id=None,
):
    """
    The same mechanism that is used in the processing of actuator commands,
    only adapted for the internal needs of the bot.
    (Main menu commands)
    """
    mediator = MediatorDependency.mediator
    cmd_fill_status = cmd.fill_status

    if cmd_fill_status == ArgumentsFillStatus.FILLED:
        try:
            await callback(**cmd.filled_args)
        except NoSuchUser:
            await mediator.send(
                message_fabric(dict(chat_id=state.chat, text=UNKNOWN_USER))
            )
        await state.reset_state()
    elif cmd_fill_status == ArgumentsFillStatus.NOT_FILLED:
        await state_storage.update_data(
            user=cmd.user_id,
            chat=cmd.user_id,
            cmd=cmd,
            callback=callback
        )
        new_kwargs = await cmd.get_next_step()
        message_kwargs.update(new_kwargs)
        # Arguments input state:
        await Command.argument_internal.set()
        await mediator.send(message_fabric(message_kwargs))

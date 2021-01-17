from typing import Callable, Optional

from aiogram.dispatcher import FSMContext

from core.bot.state_enums import ArgumentsFillStatus
from core.bot.states import Command
from core.bot.handlers.actuator_commands._command import InternalCommand
from core.bot.telegram_api import state_storage, telegram_api_dispatcher as d
from core.inbox.messages import message_fabric


async def start_cmd_internal_workflow(
    state: FSMContext,
    cmd: InternalCommand,
    message_kwargs,
    fill_status,
    callback: Optional[Callable],
    message_id=None,
):
    """
    Тот же механизм, что используется в обработке команд актуатора,
    только приспособленный для внутренних нужд бота.
    (Команды главного меню)
    """
    cmd_fill_status = cmd.fill_status

    if cmd_fill_status == ArgumentsFillStatus.FILLED:
        # Команда заполнена
        await callback(cmd.filled_args)
        await state.reset_state()
    elif cmd_fill_status == ArgumentsFillStatus.NOT_FILLED:
        # Команда не заполнена:
        await state_storage.update_data(
            user=cmd.user_id,
            chat=cmd.user_id,
            cmd=cmd,
            callback=callback
        )
        message_kwargs.update(cmd.get_next_step())
        # Arguments input state:
        await Command.argument_internal.set()
        await d.observer.send(message_fabric(message_kwargs))

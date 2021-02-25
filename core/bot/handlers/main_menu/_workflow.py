from typing import Callable, Optional

from aiogram.dispatcher import FSMContext

from core.bot.state_enums import ArgumentsFillStatus
from core.bot.states import Command
from core.bot.handlers.actuator_commands.command import InternalCommand
from core.bot.telegram_api import state_storage
from core.inbox.messages import message_fabric
from core.repository.exceptions import NoSuchUser


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
    from mediator import mediator
    cmd_fill_status = cmd.fill_status

    if cmd_fill_status == ArgumentsFillStatus.FILLED:
        # Команда заполнена
        try:
            await callback(**cmd.filled_args)
        except NoSuchUser:
            # Коллбеки вызываются только здесь.
            # Значит имеет смысл ловить исключения тоже здесь
            await mediator.telegram_dispatcher.bot.send_message(
                # TODO: заменить на mediator.send_message
                chat_id=state.chat,
                text="Неизвестный пользователь"
            )
        await state.reset_state()
    elif cmd_fill_status == ArgumentsFillStatus.NOT_FILLED:
        # Команда не заполнена:
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

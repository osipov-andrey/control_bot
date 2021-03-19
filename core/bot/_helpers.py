from dataclasses import dataclass
from functools import wraps
from typing import List, Optional

from aiogram import types
from aiogram.dispatcher import FSMContext


@dataclass
class MenuTextButton:
    cmd: str
    description: str
    admin_only: bool = False


def get_menu(*, commands: List[MenuTextButton], header="", is_admin=False):
    if header:
        header = f"<b>{header}</b>\n"
    menu = "\n".join(
        f"/{command.cmd} - {command.description}"
        for command in commands if _show_command(is_admin, command.admin_only)
    )
    menu = header + menu
    return menu


def delete_cmd_prefix(arg: str):
    """ Для быстрого ввода аргументов могут использоваться команды """
    if arg.startswith('/'):
        arg = arg[1:]
    return arg


def _show_command(is_admin: bool, is_admin_only: bool) -> bool:
    if is_admin and is_admin_only:
        return True
    if is_admin_only:
        return False
    return True


def admin_only_method(method):
    """
    Декоратор для обработчиков команд.
    Закрывает доступ к обработчикам для не-администраторов.

    В командах актуаторов своя логика разграничения доступа,
    т.к. команды не известны боту.

    Данный декоратор предназначен для ограничения доступа
    к описанным в коде бота обработчикам.
    """

    @wraps(method)
    async def wrapper(handler_instance, message: types.Message, state: FSMContext, *args, **kwargs):
        if handler_instance.is_admin is True:
            return await method(handler_instance, message, state, *args, **kwargs)
        await state.reset_state()
        return

    return wrapper

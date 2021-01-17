from collections import namedtuple
from typing import List

MenuTextButton = namedtuple("MenuTextButton", "cmd, description")


# def menu_command(cmd, description):
#     """ Текстовая команда в телеграм """
#     return f"/{cmd} - {description}"


def get_menu(*, commands: List[MenuTextButton], header=""):
    if header:
        header += '\n'
    menu = "\n".join(f"/{command.cmd} - {command.description}" for command in commands)
    menu = header + menu + "\n\n/cancel - отмена текущего действия"
    return menu


def delete_cmd_prefix(arg: str):
    """ Для быстрого ввода аргументов могут использоваться команды """
    if arg.startswith('/'):
        arg = arg[1:]
    return arg

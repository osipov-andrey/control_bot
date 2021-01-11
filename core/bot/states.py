from aiogram.dispatcher.filters.state import State, StatesGroup


class Command(StatesGroup):
    client = State()
    command = State()
    arguments = State()


class MainMenu(StatesGroup):
    main_menu = State()
    users = State()
    me = State()

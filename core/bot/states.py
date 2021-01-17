from aiogram.dispatcher.filters.state import State, StatesGroup


class Command(StatesGroup):
    client = State()
    command = State()
    arguments = State()
    argument_internal = State()


class MainMenu(StatesGroup):
    main_menu = State()
    users = State()
    # users = MainMenuUsers()
    me = State()

from aiogram.dispatcher.filters.state import State, StatesGroup


class Command(StatesGroup):
    client = State()
    command = State()
    arguments = State()

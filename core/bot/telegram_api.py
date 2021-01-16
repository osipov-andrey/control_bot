import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import config


__all__ = ['telegram_api_dispatcher', 'state_storage']

_API_TOKEN = config["API_TOKEN"]

_bot = aiogram.Bot(token=_API_TOKEN)
state_storage = MemoryStorage()
telegram_api_dispatcher = aiogram.Dispatcher(bot=_bot, storage=state_storage)

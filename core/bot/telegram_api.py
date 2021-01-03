import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from core.config import config


__all__ = ['telegram_api_dispatcher']

_API_TOKEN = config["API_TOKEN"]

_bot = aiogram.Bot(token=_API_TOKEN)
storage = MemoryStorage()
telegram_api_dispatcher = aiogram.Dispatcher(bot=_bot, storage=storage)

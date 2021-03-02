import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from core.config import config


__all__ = ['telegram_api_dispatcher', 'state_storage']

_API_TOKEN = config["API_TOKEN"]

_bot = aiogram.Bot(token=_API_TOKEN)
state_storage = MemoryStorage()


class CustomDispatcher(aiogram.Dispatcher):

    def class_message_handler(self, *custom_filters, commands=None, regexp=None, content_types=None, state=None,
                              run_task=None, **kwargs):
        """ Register Class as message handler """
        def decorator(class_):
            handler = class_()

            self.register_message_handler(handler.callback, *custom_filters,
                                          commands=commands, regexp=regexp, content_types=content_types,
                                          state=state, run_task=run_task, **kwargs)
            return class_

        return decorator

    def class_callback_query_handler(self, *custom_filters, state=None, run_task=None, **kwargs):
        """ Register Class as callback query handler """
        def decorator(class_):
            handler = class_()
            self.register_callback_query_handler(handler.callback, *custom_filters,
                                                 state=state, run_task=run_task, **kwargs)
            return class_

        return decorator


telegram_api_dispatcher = CustomDispatcher(bot=_bot, storage=state_storage)

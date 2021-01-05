import json
from abc import ABC
from typing import Tuple

from ._descriptors import *


def message_fabric(raw_message: bytes):
    message_body = raw_message.decode()
    message_body = json.loads(message_body)

    if "document" in message_body:
        return DocumentMessage(message_body)
    elif "image" in message_body:
        return PhotoMessage(message_body)
    else:
        return TelegramLeverMessage(message_body)


class BaseMessage(ABC):
    PARAMS_TO_SENT: Tuple[str]

    target = MessageTargetDescriptor()
    buttons = InlineButtonsDescriptor()

    def __init__(self, message_body: dict):

        for key, value in message_body.items():
            setattr(self, key, value)

    def get_params_to_sent(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if key in self.PARAMS_TO_SENT}

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def __str__(self):
        values = '\n'.join(f'{key}: {value}' for key, value in self.__dict__.items())
        return f"\n{'#'*20} TelegramLeverMessage {'#'*20}" \
               f"\n{values}" \
               f"\n{'#'*20}{' '*22}{'#'*20}"


class TelegramLeverMessage(BaseMessage):
    PARAMS_TO_SENT = ('chat_id', 'text', 'entities', 'reply_markup')

    message = MessageTextDescriptor()


class DocumentMessage(BaseMessage):
    PARAMS_TO_SENT = ('chat_id', 'document', 'caption', 'reply_markup')

    document = DocumentDescriptor()


class PhotoMessage(BaseMessage):
    PARAMS_TO_SENT = ('chat_id', 'photo', 'caption', 'reply_markup')

    image = PhotoDescriptor()
    message = CaptionDescriptor()




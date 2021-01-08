import json
from abc import ABC

from ._descriptors import *


def message_fabric(raw_message: Union[bytes, dict]):
    # TODO: ugly
    if isinstance(raw_message, bytes):
        message_body = raw_message.decode()
        message_body = json.loads(message_body)
    elif isinstance(raw_message, dict):
        message_body = raw_message
    else:
        raise AttributeError("Unsupported raw_message type!")

    if "document" in message_body:
        return DocumentMessage(message_body)
    elif "image" in message_body:
        return PhotoMessage(message_body)
    elif message_body["target"].get("message_id") is not None:
        return EditTextMessage(message_body)
    else:
        return TextMessage(message_body)


class BaseMessage(ABC):
    _COMMON_PARAMS_TO_SENT = ('chat_id', 'reply_markup', 'parse_mode', 'reply_to_message_id')
    _PARAMS_TO_SENT = tuple()

    target = MessageTargetDescriptor()
    buttons = InlineButtonsDescriptor()
    issue = MessageIssue()
    # replies = MessageReplies()

    def __init__(self, message_body: dict):
        self.parse_mode = 'HTML'
        for key, value in message_body.items():
            setattr(self, key, value)

    def get_params_to_sent(self, only_common=False) -> dict:
        """ Собирает параметры для отправки сообщения через aiogram """
        if only_common:
            params = self._COMMON_PARAMS_TO_SENT
        else:
            params = self._COMMON_PARAMS_TO_SENT + self._PARAMS_TO_SENT
        return {key: value for key, value in self.__dict__.items() if key in params}

    def prepare_replies(self, reply_to_message_id) -> List['BaseMessage']:
        replies = []
        for reply in self.replies:
            reply: dict
            message_kwargs = self.get_params_to_sent(only_common=True)
            message_kwargs.update(reply)
            message_kwargs["reply_to_message_id"] = reply_to_message_id
            message_kwargs["target"] = self.target
            reply_message = message_fabric(message_kwargs)
            replies.append(reply_message)
        return replies

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def __str__(self):
        values = '\n'.join(f'{key}: {value}' for key, value in self.__dict__.items())
        return f"\n{'#'*20} TelegramLeverMessage {'#'*20}" \
               f"\n{values}" \
               f"\n{'#'*20}{' '*22}{'#'*20}"


class TextMessage(BaseMessage):
    _PARAMS_TO_SENT = ('text', 'entities')

    message = MessageTextDescriptor()


class EditTextMessage(TextMessage):
    _PARAMS_TO_SENT = ('text', 'entities', 'message_id')


class DocumentMessage(BaseMessage):
    _PARAMS_TO_SENT = ('document', 'caption')

    document = DocumentDescriptor()


class PhotoMessage(BaseMessage):
    _PARAMS_TO_SENT = ('photo', 'caption')

    image = PhotoDescriptor()
    message = CaptionDescriptor()

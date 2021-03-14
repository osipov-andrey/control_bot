from abc import ABC
from dataclasses import asdict

from ._descriptors import *


def create_message(
        target: MessageTarget,
        text: str,
        # Add new parameters as needed
) -> 'BaseMessage':
    """
    Adapter for build messages with message fabric
    """
    return inbox_message_fabric(
        dict(
            target=asdict(target),
            text=text
        )
    )


def inbox_message_fabric(message_body: dict) -> 'BaseMessage':
    """
    We receive a message from the actuator in the form of a dictionary.
    That's why we need this factory.
    """
    target = message_body["target"]

    if "document" in message_body:
        return DocumentMessage(message_body)
    elif "image" in message_body:
        return PhotoMessage(message_body)
    elif target.get("message_id") is not None:
        return EditTextMessage(message_body)
    else:
        return TextMessage(message_body)


class BaseMessage(ABC):
    _COMMON_PARAMS_TO_SENT = ('chat_id', 'reply_markup', 'parse_mode', 'reply_to_message_id')
    _PARAMS_TO_SENT = tuple()

    target = MessageTargetDescriptor()
    reply_markup = InlineButtonsDescriptor()
    issue = MessageIssue()

    def __init__(self, message_body: dict):
        self.parse_mode = 'HTML'
        for key, value in message_body.items():
            setattr(self, key, value)

    def get_params_to_sent(self, only_common=False) -> dict:
        """ Gathers parameters for sending a message via aiogram """
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
            message_kwargs["target"] = asdict(self.target)
            reply_message = inbox_message_fabric(message_kwargs)
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


class EditTextMessage(TextMessage):
    _PARAMS_TO_SENT = ('text', 'entities', 'message_id')


class DocumentMessage(BaseMessage):
    _PARAMS_TO_SENT = ('document', 'caption')

    document = DocumentDescriptor()


class PhotoMessage(BaseMessage):
    _PARAMS_TO_SENT = ('photo', 'caption')

    image = PhotoDescriptor()
    message = CaptionDescriptor()

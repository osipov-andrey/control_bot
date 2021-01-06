import base64
import io
from typing import List, Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile

from core._helpers import MessageTarget, TargetTypes


class MessageTargetDescriptor:

    def __set__(self, instance, value: Union[dict, MessageTarget]):
        if isinstance(value, dict):
            target = MessageTarget(**value)
        elif isinstance(value, MessageTarget):
            target = value
        else:
            raise AttributeError(f"Unsupported target value: {type(value)}")
        instance.__dict__["target"] = target

        if target.target_type == TargetTypes.USER.value:
            instance.__dict__["chat_id"] = target.target_name


class InlineButtonsDescriptor:

    def __set__(self, instance, value: List[dict]):
        # TODO: изменить параметр в telegram_lever с 'buttons' на 'reply_markup'
        instance.__dict__["reply_markup"] = self._generate_inline_buttons(value)

    @staticmethod
    def _generate_inline_buttons(buttons: List[dict]) -> InlineKeyboardMarkup:
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        for button in buttons:
            inline_keyboard.insert(InlineKeyboardButton(**button))
        return inline_keyboard


class MessageTextDescriptor:

    def __set__(self, instance, value: str):
        # TODO: изменить параметр в telegram_lever с 'message' на 'text'
        instance.__dict__["text"] = value


class MessageCaptionDescriptor:

    def __set__(self, instance, value):
        instance.__dict__["caption"] = value


class DocumentDescriptor:

    def __set__(self, instance, value: dict):
        # TODO: валидация параметров в value
        content = value["content"]
        filename = value["filename"]
        caption = value["caption"]

        text_file = InputFile(
            io.StringIO(content),
            filename=filename
        )
        instance.__dict__["document"] = text_file
        instance.__dict__["caption"] = caption


class PhotoDescriptor:

    def __set__(self, instance, value):
        instance.__dict__["photo"] = base64.b64decode(value)


class CaptionDescriptor:

    def __set__(self, instance, value):
        instance.__dict__["caption"] = value


# class MessageReplies:
#
#     def __set__(self, instance, value):
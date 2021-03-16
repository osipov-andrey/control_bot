import base64
import io
from typing import List, Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, InputFile

from .._helpers import MessageTarget, TargetType
from core.mediator.dependency import MediatorDependency


class MessageTargetDescriptor:

    def __set__(self, instance, value: dict):
        target = MessageTarget(**value)

        instance.__dict__["target"] = target

        if target.target_type == TargetType.USER.value:
            instance.__dict__["chat_id"] = target.target_name
            instance.__dict__["message_id"] = target.message_id


class InlineButtonsDescriptor:

    def __set__(self, instance, value: Union[ReplyKeyboardMarkup, List[dict]]):
        if isinstance(value, ReplyKeyboardMarkup):
            instance.__dict__["reply_markup"] = value
        else:
            instance.__dict__["reply_markup"] = self._generate_inline_buttons(value)

    @staticmethod
    def _generate_inline_buttons(buttons: List[dict]) -> InlineKeyboardMarkup:
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        for button in buttons:
            inline_keyboard.insert(InlineKeyboardButton(**button))
        return inline_keyboard


class MessageCaptionDescriptor:

    def __set__(self, instance, value):
        instance.__dict__["caption"] = value


class DocumentDescriptor:

    def __set__(self, instance, value: dict):
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

    def __set__(self, instance, value: bytes):
        instance.__dict__["photo"] = base64.b64decode(value)


class CaptionDescriptor:

    def __set__(self, instance, value: str):
        instance.__dict__["caption"] = value


class MessageIssueDescriptor:

    def __set__(self, instance, value: dict):

        if value["resolved"] is True:
            problem_issue = MediatorDependency.mediator.memory_storage.resolve_issue(value["issue_id"])
            if problem_issue:
                instance.__dict__["reply_to_message_id"] = problem_issue.reply_to_message_id
        instance.__dict__["issue"] = value

    def __get__(self, instance, owner):
        if isinstance(instance.__dict__.get("issue"), self.__class__):
            return
        return instance.__dict__.get("issue")


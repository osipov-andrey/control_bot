import base64
import io
from typing import Optional, Tuple, Union
from typing import List

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    InputFile,
)

from core.mediator.dependency import MediatorDependency as md
from .models import ActuatorMessage, TargetType, Issue


def create_message_from_inbox(message: ActuatorMessage, **kwargs) -> "OutgoingMessage":
    """
    We receive a message from the actuator in the form of a pydantic model 'ActuatorMessage'.
    That's why we need this factory.
    """

    message_kwargs: dict = message.dict()
    if kwargs:
        message_kwargs.update(kwargs)

    message = ActuatorMessage(**message_kwargs)

    target_type = message.target.target_type
    if target_type != TargetType.USER.value:
        raise ValueError(f"Unsupported message type for outgoing message! [{target_type}]")
    message_kwargs["chat_id"] = message.target.target_name
    message_kwargs["to_message_id"] = message.target.message_id

    reply_markup = message_kwargs.get("reply_markup")
    if reply_markup:
        message_kwargs["reply_markup"] = _generate_inline_buttons(reply_markup)

    return OutgoingMessage(**message_kwargs)


class OutgoingMessage:
    """Message to send to Telegram API"""

    _COMMON_PARAMS_TO_SENT: Tuple[str, ...] = ("chat_id", "reply_markup", "parse_mode")
    _PARAMS_TO_SENT: Tuple[str, ...] = tuple()

    def __new__(cls, *args, **kwargs):
        if kwargs.get("document"):
            msg = object.__new__(DocumentMessage)
        elif kwargs.get("image"):
            msg = object.__new__(PhotoMessage)
        elif kwargs.get("to_message_id"):
            # We get the "message id" for each event update from the Telegram-API.
            # Here parameter changed to avoid confusion
            msg = object.__new__(EditTextMessage)
        else:
            msg = object.__new__(TextMessage)
        return msg

    def __init__(
            self,
            *,
            chat_id: str,
            reply_markup: Optional[Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]] = None,
            reply_to_message_id: Optional[int] = None,
            parse_mode: str = "HTML",
            replies: Optional[list] = None,
            issue: Optional[dict] = None,
            **kwargs,
    ):
        self.chat_id = chat_id
        self.reply_markup = reply_markup
        self.reply_to_message_id = reply_to_message_id
        self.parse_mode = parse_mode
        self.replies: list = replies if replies else []
        self.issue = issue
        if issue:
            self._check_issue(issue)

    def get_params_to_sent(self, only_common=False) -> dict:
        """Gathers parameters for sending a message via aiogram"""
        if only_common:
            params = self._COMMON_PARAMS_TO_SENT
        else:
            params = self._COMMON_PARAMS_TO_SENT + self._PARAMS_TO_SENT
        return {key: value for key, value in self.__dict__.items() if key in params}

    def get_replies(self, reply_to_message_id) -> List["OutgoingMessage"]:
        """
        Generate message object for replies.
        :param reply_to_message_id - message id in chat
        """
        replies = []
        for reply in self.replies:  # type: dict
            message_kwargs = self.get_params_to_sent(only_common=True)
            message_kwargs.update(reply)
            message_kwargs["reply_to_message_id"] = reply_to_message_id
            reply_message = OutgoingMessage(**message_kwargs)
            replies.append(reply_message)
        return replies

    def _check_issue(self, issue: dict):
        if issue.get("resolved"):
            problem_issue: Optional[Issue] = md.get_mediator().memory_storage.resolve_issue(issue.get("issue_id", ""))
            if problem_issue:
                self.reply_to_message_id = problem_issue.reply_to_message_id

    def __str__(self):
        values = "\n".join(f"{key}: {value}" for key, value in self.__dict__.items())
        return (
            f"\n{'#' * 20} TelegramLeverMessage {'#' * 20}"
            f"\n{values}"
            f"\n{'#' * 20}{' ' * 22}{'#' * 20}"
        )


class TextMessage(OutgoingMessage):
    """Message only with text"""

    _PARAMS_TO_SENT = ("text", "reply_to_message_id")

    def __init__(self, *, text: str, **kwargs):
        super().__init__(**kwargs)
        self.text = text


class EditTextMessage(TextMessage):
    """Message that will edit an existing one"""

    _PARAMS_TO_SENT = ("text", "message_id")

    def __init__(self, *, to_message_id: int, **kwargs):
        super().__init__(**kwargs)
        self.message_id = to_message_id


class DocumentMessage(OutgoingMessage):
    """Message with document"""

    _PARAMS_TO_SENT = ("document", "caption", "reply_to_message_id")

    def __init__(self, *, document: dict, **kwargs):
        super().__init__(**kwargs)
        self.document, self.caption = self._get_document(document)

    @staticmethod
    def _get_document(document: dict) -> Tuple[InputFile, str]:
        content: str = document.get("content", "")
        filename: str = document.get("filename", "_empty_name_.txt")
        caption: str = document.get("caption", "")

        text_file: InputFile = InputFile(io.StringIO(content), filename=filename)
        return text_file, caption


class PhotoMessage(OutgoingMessage):
    """Message with image"""

    _PARAMS_TO_SENT = ("photo", "caption", "reply_to_message_id")

    def __init__(self, *, image: str, text: str, **kwargs):
        super().__init__(**kwargs)
        self.photo = base64.b64decode(image)
        self.caption = text


def _generate_inline_buttons(buttons: List[dict]) -> InlineKeyboardMarkup:
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    for button in buttons:
        inline_keyboard.insert(InlineKeyboardButton(**button))
    return inline_keyboard

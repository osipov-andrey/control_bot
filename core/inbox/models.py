import datetime
from enum import Enum
from typing import Optional, List, Dict, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator


class TargetType(Enum):
    SERVICE = "service"
    USER = "user"
    CHANNEL = "channel"


class InlineButton(BaseModel):
    """Inline button description"""

    text: str
    callback_data: str

    @validator("callback_data")
    def callback_data_must_be_a_command(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("Callback data not a command!")
        return value


class Reply(BaseModel):
    """Reply to the base message"""

    image: Optional[str] = None  # Base64
    text: Optional[str] = None

    @root_validator
    def not_empty_reply(cls, values: dict):
        if not (values.get("image") or values.get("text")):
            raise ValueError("Empty reply!")
        return values


class ArgSchema(BaseModel):
    """
    Command argument schema for
    validation argument value in Cerberus
    """

    type: str
    max: Optional[int] = None
    min: Optional[int] = None
    regex: Optional[str] = None
    allowed: Optional[list] = None

    def dict(self, *args, **kwargs):
        d: dict = super().dict(*args, **kwargs)
        return {key: value for key, value in d.items() if value}


class ArgInfo(BaseModel):
    """Actuator command argument description"""

    description: str
    arg_schema: ArgSchema
    options: Optional[list] = None
    is_user: Optional[bool] = False
    is_actuator: Optional[bool] = False
    is_granter: Optional[bool] = False
    is_channel: Optional[bool] = False
    is_subscriber: Optional[bool] = False


class CommandBehavior(BaseModel):
    """The Actuator command can have different behaviors"""

    description: str
    args: Optional[Dict[str, ArgInfo]] = None


class CommandSchema(BaseModel):
    """
    Description of the actuator command.
    Received when the actuator is plugged on.
    """

    hidden: bool
    behavior__admin: Optional[CommandBehavior] = None
    behavior__user: Optional[CommandBehavior] = None

    @root_validator
    def must_have_at_least_one_behavior(cls, values: dict):
        if not (values.get("behavior__admin") or values.get("behavior__user")):
            raise ValueError("Empty behaviors!")
        return values


class Issue(BaseModel):
    """Notification of the occurrence or resolution of a problem"""

    issue_id: str
    resolved: bool
    reply_to_message_id: Optional[int] = None
    time_: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now())


class Document(BaseModel):
    content: str
    filename: str
    caption: str


class MessageTarget(BaseModel):
    target_type: str
    target_name: Union[str, int]
    message_id: Optional[str] = None

    @validator("target_type")
    def allowed_target_types(cls, value: str) -> str:
        allowed = [v.value for v in TargetType.__members__.values()]
        if not value.lower() in allowed:
            raise ValueError(f"Target type {value} not in allowed: {allowed}!")
        return value


class ActuatorMessage(BaseModel):
    """
    MAIN MODEL.
    Incoming message from actuator
    """

    _id: UUID
    cmd: str
    target: MessageTarget
    sender_name: Optional[str] = None
    subject: Optional[str] = None
    text: Optional[str] = None
    image: Optional[str] = None  # Base64
    document: Optional[Document] = None
    issue: Optional[Issue] = None
    commands: Optional[Dict[str, CommandSchema]] = None
    replies: Optional[List[Reply]] = None
    reply_markup: Optional[List[InlineButton]] = None
    inline_edit_button: bool = False

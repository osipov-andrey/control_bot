import datetime
from collections import namedtuple
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Union


class TargetType(Enum):
    SERVICE = "service"
    USER = "user"
    CHANNEL = "channel"


class ArgType(Enum):
    STR = "string"
    INT = "integer"
    LIST = "list"
    # USER = "user"


class Behavior(Enum):
    USER = "user"
    ADMIN = "admin"
    SERVICE = "service"


@dataclass
class MessageTarget:
    target_type: TargetType
    target_name: Union[str, int]
    message_id: Optional[str] = None


@dataclass
class CommandBehavior:
    description: str
    args: Dict[str, Union['ArgScheme', dict]]

    def __post_init__(self):
        self.args = {
            arg_name: ArgScheme(**arg_info)
            for arg_name, arg_info in self.args.items()
        }


@dataclass
class CommandSchema:
    hidden: bool
    behavior__admin: Optional[Union['CommandBehavior', dict]] = None
    behavior__user: Optional[Union['CommandBehavior', dict]] = None

    def __post_init__(self):
        if self.behavior__admin:
            self.behavior__admin = CommandBehavior(**self.behavior__admin)
        if self.behavior__user:
            self.behavior__user = CommandBehavior(**self.behavior__user)


@dataclass
class ArgScheme:
    description: str
    schema: dict
    options: Optional[list] = None
    is_user: Optional[bool] = False
    is_actuator: Optional[bool] = False
    is_granter: Optional[bool] = False
    is_channel: Optional[bool] = False
    is_subscriber: Optional[bool] = False


def get_log_cover(cover_name: str) -> str:
    cover = f"\n{'#'*20} {cover_name} {'#'*20}" \
            f"\n%s" \
            f"\n{'#'*20} {' '*len(cover_name)} {'#'*20}"
    return cover


@dataclass
class Issue:
    issue_id: str
    resolved: bool
    reply_to_message_id: int
    time_: datetime.datetime = field(init=False)

    def __post_init__(self):
        self.time_ = datetime.datetime.now()

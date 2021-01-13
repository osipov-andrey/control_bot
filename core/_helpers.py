import datetime
from collections import namedtuple
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union


class TargetTypes(Enum):
    SERVICE = "service"
    USER = "user"
    CHANNEL = "channel"


class ArgTypes(Enum):
    STR = "string"
    INT = "integer"
    LIST = "list"
    # USER = schema["is_client"]


# TODO: replace with dataclass?
MessageTarget = namedtuple(
    "MessageTarget",
    "target_type, target_name, message_id", defaults=(None, )
)


# CommandScheme = namedtuple(
#     "CommandScheme",
#     "description, hidden, admin_only, args"
# )
@dataclass
class CommandBehavior:
    description: str
    # hidden: bool
    # admin_only: bool
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
    # description: str
    # admin_only: bool
    # args: Dict[str, Union['ArgScheme', dict]]

    def __post_init__(self):
        if self.behavior__admin:
            self.behavior__admin = CommandBehavior(**self.behavior__admin)
        if self.behavior__user:
            self.behavior__user = CommandBehavior(**self.behavior__user)
        # self.args = {
        #     arg_name: ArgScheme(**arg_info)
        #     for arg_name, arg_info in self.args.items()
        # }


ArgScheme = namedtuple(
    "ArgScheme",
    "description, schema, options", defaults=(None, )
)


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

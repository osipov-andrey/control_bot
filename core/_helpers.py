import datetime
from collections import namedtuple
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Union


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
class CommandScheme:
    description: str
    hidden: bool
    admin_only: bool
    args: Dict[str, Union['ArgScheme', dict]]

    def __post_init__(self):
        self.args = {
            arg_name: ArgScheme(**arg_info)
            for arg_name, arg_info in self.args.items()
        }


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

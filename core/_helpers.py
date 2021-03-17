import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union


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


"""
Command information models for validation and use in code.
This information is sent by the actuator when connected.
"""

from typing import Dict, Optional, Union

from pydantic.dataclasses import dataclass as pdataclass


@pdataclass
class ArgSchema:
    type: str
    max: Optional[int] = None
    min: Optional[int] = None
    regex: Optional[str] = None
    allowed: Optional[list] = None


@pdataclass
class ArgInfo:
    description: str
    arg_schema: ArgSchema
    options: Optional[list] = None
    is_user: Optional[bool] = False
    is_actuator: Optional[bool] = False
    is_granter: Optional[bool] = False
    is_channel: Optional[bool] = False
    is_subscriber: Optional[bool] = False
    cerberus_schema: Optional[dict] = None

    def __post_init_post_parse__(self):
        # For use this field in Cerberus
        self.cerberus_schema = {
            key: value for key, value in self.arg_schema.__dict__.items()
            if value and not key.startswith("_")
        }


@pdataclass
class CommandBehavior:
    description: str
    args: Optional[Dict[str, ArgInfo]]


@pdataclass
class CommandSchema:
    hidden: bool
    behavior__admin: Optional[CommandBehavior] = None
    behavior__user: Optional[CommandBehavior] = None

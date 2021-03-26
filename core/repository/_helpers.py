from collections import namedtuple
from typing import Type

from sqlalchemy import Table


def create_mapping(table: Table) -> Type[tuple]:
    fields = table.c.keys()
    name: str = to_pascal_case(table.name)
    mapping = namedtuple(name, fields)
    return mapping


def to_pascal_case(snake_case: str) -> str:
    parts = snake_case.split("_")
    pascal = "".join(part.capitalize() for part in parts)
    return pascal

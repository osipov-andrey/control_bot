from collections import namedtuple

from sqlalchemy import Table


def create_mapping(table: Table) -> namedtuple:
    fields = table.c.keys()
    name = to_camel_case(table.name)
    mapping = namedtuple(name, fields)
    return mapping


def to_camel_case(kebab_case: str) -> str:
    parts = kebab_case.split('_')
    kebab = "".join(part.capitalize() for part in parts)
    return kebab

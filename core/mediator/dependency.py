from typing import Optional

from core.mediator.mediator_proto import MediatorProto


class MediatorDependency:
    """Class for accessing the Mediator"""

    _mediator: Optional[MediatorProto] = None

    @classmethod
    def set_mediator(cls, mediator: MediatorProto) -> None:
        cls._mediator = mediator
        # Since the mediator is injected dynamically

    @classmethod
    def get_mediator(cls) -> MediatorProto:
        if not cls._mediator:
            raise RuntimeError("Need to set mediator!")
        return cls._mediator

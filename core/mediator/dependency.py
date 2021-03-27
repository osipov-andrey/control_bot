from core.mediator import Mediator


class MediatorDependency:
    """ Class for accessing the Mediator """

    mediator: Mediator  # type: ignore

    @classmethod
    def add_mediator(cls, mediator: Mediator):
        cls.mediator: Mediator = mediator
        # Since the mediator is injected dynamically

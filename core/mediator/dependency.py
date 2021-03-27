class MediatorDependency:
    """ Class for accessing the Mediator """

    mediator = None  # type: ignore

    @classmethod
    def add_mediator(cls, mediator):
        cls.mediator = mediator
        # Since the mediator is injected dynamically

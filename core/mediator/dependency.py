class MediatorDependency:
    """ Class for accessing the Mediator """
    mediator = None

    @classmethod
    def add_mediator(cls, mediator):
        cls.mediator = mediator

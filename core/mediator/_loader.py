""" Dark magic here """
import importlib.util
import importlib.abc
import pathlib
import sys
from importlib._bootstrap_external import SourceFileLoader


class MediatorPathFinder(importlib.abc.MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        if fullname != "mediator":
            return
        path = pathlib.Path(__file__).parent.absolute()
        path_to_mediator = path.joinpath("_mediator.py")
        module_hierarchy = f"{__package__}.mediator"

        module = importlib.util.spec_from_file_location(
            name=module_hierarchy, location=path_to_mediator,
            loader=MediatorLoader(str(module_hierarchy), str(path_to_mediator))
        )

        return module


class MediatorLoader(SourceFileLoader):
    mediator = None  # SINGLETON !

    @classmethod
    def save_mediator(cls, mediator):
        cls.mediator = mediator

    def exec_module(self, module):
        if self.mediator is None:
            super().exec_module(module)
            mediator = module.Mediator()
            module.mediator = mediator
            self.save_mediator(mediator)
        else:
            module.mediator = self.mediator


sys.meta_path.append(MediatorPathFinder())

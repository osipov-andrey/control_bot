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
    module = None

    @classmethod
    def set_module(cls, module):
        cls.module = module

    def exec_module(self, module):
        if self.module is None:
            # SINGLETON !
            super().exec_module(module)
            module.mediator = module.Mediator()
            self.set_module(module)
        else:
            module.mediator = self.module.mediator


sys.meta_path.append(MediatorPathFinder())

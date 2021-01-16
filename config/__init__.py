import pathlib
import yaml


root = pathlib.Path(__file__).parent.absolute()
with open(root.joinpath("config.yaml"), "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

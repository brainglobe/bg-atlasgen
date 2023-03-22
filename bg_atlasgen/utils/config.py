from importlib.resources import open_text

import yaml

from bg_atlasgen.component_gen import config


def load_config(yaml_file):
    with open_text(config, yaml_file) as file:
        data = yaml.safe_load(file)
        return data

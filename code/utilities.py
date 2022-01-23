import os
import json
from pathlib import Path

## Config
os.environ = {}
CONFIG_OPTIONS = {}                     # This'll be populated on import
CONFIG_NAME = "config.json"	            # The name of the config file
DEV_CONFIG_NAME = "config.dev.json"     # The name of the dev config file (overrides properties stored in the normal and prod config files)
PROD_CONFIG_NAME = "config.prod.json"   # The name of the prod config file (overrides properties stored in the normal config file)
DIRS_FROM_ROOT = 1			            # How many directories away this script is from the root


def get_root_path() -> Path:
    path = Path(__file__)

    for _ in range(DIRS_FROM_ROOT + 1):  # the '+ 1' includes this script in the path
        path = path.parent

    return path


def load_json(path: Path) -> dict:
    with open(path) as fd:
        return json.load(fd)


def save_json(path: Path, data: dict):
    with open(path, 'w') as fd:
        json.dump(data, fd)


def load_config(directory_path: Path = None) -> dict:
    '''
    Parses one or more JSON configuration files to build a dictionary with proper precedence for configuring the program

    :param directory_path: Optional path to load configuration files from. If None, then the program's root (cwd/..) will be searched.
    :type directory_path: Path, optional
    :return: A dictionary containing key-value pairs for use in configuring parts of the program.
    :rtype: dictionary
    '''

    path = directory_path or get_root_path()

    config_path = Path.joinpath(path, CONFIG_NAME)
    if (not config_path.exists()):
        raise RuntimeError("Unable to find config.json file in root!")

    config = load_json(config_path)

    ## Override the config values if the prod config file exists.
    prod_config_path = Path.joinpath(path, PROD_CONFIG_NAME)
    if (prod_config_path.exists()):
        prod_config = load_json(prod_config_path)

        for key, value in prod_config.items():
            config[key] = value

    ## Override the config values if the dev config file exists.
    dev_config_path = Path.joinpath(path, DEV_CONFIG_NAME)
    if (dev_config_path.exists()):
        dev_config = load_json(dev_config_path)

        for key, value in dev_config.items():
            config[key] = value

    return config


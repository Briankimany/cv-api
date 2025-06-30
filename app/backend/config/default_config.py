
import os
import yaml
from pathlib import Path


APP_DIR = Path(__file__).parent.parent.parent.parent

APP_DATA_PATH = APP_DIR /'app-data'
APP_DATA_PATH.mkdir(parents=True,exist_ok=True)
CONFIG_FILE_PATH = APP_DATA_PATH /'config.yaml'

db_folder = APP_DATA_PATH /'db'
db_folder.mkdir(parents=True,exist_ok=True)

DEFAULT_CONFIG = {
    "database_url": f"sqlite:///{str(db_folder.absolute())}/user_data.db",
    "loggers": {
        "database": {
            "name": "database_manager",
            "path": "logs/database.log",
            "level": "DEBUG",
            "stream":False
        },
        "api": {
            "name": "api_manager",
            "path": "logs/api.log",
            "level": "DEBUG",
            "stream":True
        },
        "access": {
            "name": "access_manager",
            "path": "logs/access.log",
            "level": "DEBUG",
            "stream":True
        },
        "test": {
            "name": "test_manager",
            "path": "logs/tests.log",
            "level": "DEBUG",
            "stream": False
        }
    }
}


def create_default_config(config_path: str = "config.yaml"):
    """
    Create a default YAML config file if it does not exist.

    Args:
        config_path (str): Path to the config file to create.
    """
    if os.path.exists(config_path):
        return True 

    os.makedirs(os.path.dirname(config_path) or ".", exist_ok=True)

    with open(config_path, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, sort_keys=False)

    return DEFAULT_CONFIG

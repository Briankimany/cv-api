import os
import yaml
from dataclasses import dataclass
from typing import Dict

from .default_config import create_default_config ,CONFIG_FILE_PATH ,APP_DATA_PATH,APP_DIR
from .temp_db import generate_temp_db_url


DATE_FORMAT = "%Y-%m-%d"

@dataclass
class LoggerConfig:
    name: str
    path: str
    level: str
    stream:bool=False


@dataclass
class AppConfig:
    database_url: str
    loggers: Dict[str, LoggerConfig]


def load_config(config_path: str) -> AppConfig:
    """
    Loads YAML configuration from a file.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        AppConfig: Parsed configuration object.
    """
    if not os.path.exists(config_path):
        raw_config = create_default_config(config_path)
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    loggers = {
        key: LoggerConfig(**details)
        for key, details in raw_config["loggers"].items()
    }

    return AppConfig(
        database_url=raw_config["database_url"],
        loggers=loggers
    )


CONFIG = load_config(CONFIG_FILE_PATH)
CONFIG.database_url =generate_temp_db_url() if os.getenv('IN_TESTS','').strip() == 'true' else CONFIG.database_url

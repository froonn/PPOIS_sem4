import json
import os

from constants import CONFIG_FILE, DEFAULT_DB_NAME


def _get_config_path():
    """Returns the full path to the configuration file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, CONFIG_FILE)


def load_config():
    """
    Loads configuration from the JSON file. If the file doesn't exist,
    it creates it with default values.
    """
    config_path = _get_config_path()
    if not os.path.exists(config_path):
        default_config = {"db_name": DEFAULT_DB_NAME}
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    else:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if "db_name" not in config:
                config["db_name"] = DEFAULT_DB_NAME
                save_config(config["db_name"])
            return config


def save_config(db_name):
    """
    Saves the current configuration (database name) to the JSON file.
    :param db_name: The new database file name to save.
    """
    config_path = _get_config_path()
    config = {"db_name": db_name}
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


def get_db_name():
    """Returns the current database name from the loaded configuration."""
    config = load_config()
    return config.get("db_name", DEFAULT_DB_NAME)


def set_db_name(new_db_name):
    """Sets and saves a new database name in the configuration."""
    save_config(new_db_name)


def get_config_file_path():
    """Returns the path to the config file."""
    return _get_config_path()

"""Configuration management for brag."""

import os
from pathlib import Path
from typing import Optional

import yaml


class ConfigError(Exception):
    """Raised when there's a configuration error."""

    pass


def get_brag_dir() -> Path:
    """Get the brag directory from environment variable.

    Returns:
        Path to the brag directory.

    Raises:
        ConfigError: If BRAG_DIR is not set.
    """
    brag_dir = os.environ.get("BRAG_DIR")
    if not brag_dir:
        raise ConfigError(
            "BRAG_DIR environment variable is not set.\n"
            "Please set it to the directory where you want to store your brag documents:\n"
            "  export BRAG_DIR=~/Documents/brag"
        )
    return Path(brag_dir).expanduser()


def get_config_path() -> Path:
    """Get the path to config.yaml."""
    return get_brag_dir() / "config.yaml"


def get_entries_dir() -> Path:
    """Get the path to the entries directory."""
    return get_brag_dir() / "entries"


def load_config() -> dict:
    """Load configuration from config.yaml.

    Returns:
        Configuration dictionary.

    Raises:
        ConfigError: If config file doesn't exist or is invalid.
    """
    config_path = get_config_path()
    if not config_path.exists():
        raise ConfigError(
            f"Configuration file not found at {config_path}.\n"
            "Run 'brag init' to initialize your brag directory."
        )

    with open(config_path) as f:
        config = yaml.safe_load(f) or {}

    return config


def save_config(config: dict) -> None:
    """Save configuration to config.yaml.

    Args:
        config: Configuration dictionary to save.
    """
    config_path = get_config_path()
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_topics() -> list[str]:
    """Get list of topics from config.

    Returns:
        List of topic names.
    """
    config = load_config()
    return config.get("topics", [])


def add_topic(topic: str) -> None:
    """Add a topic to the configuration.

    Args:
        topic: Topic name to add.

    Raises:
        ConfigError: If topic already exists.
    """
    config = load_config()
    topics = config.get("topics", [])

    if topic in topics:
        raise ConfigError(f"Topic '{topic}' already exists.")

    topics.append(topic)
    config["topics"] = topics
    save_config(config)


def is_initialized() -> bool:
    """Check if the brag directory is initialized.

    Returns:
        True if initialized, False otherwise.
    """
    try:
        brag_dir = get_brag_dir()
        config_path = brag_dir / "config.yaml"
        entries_dir = brag_dir / "entries"
        return config_path.exists() and entries_dir.exists()
    except ConfigError:
        return False

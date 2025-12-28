"""Unit tests for configuration management."""

from pathlib import Path

import pytest
import yaml

from brag.config import (
    ConfigError,
    add_topic,
    get_brag_dir,
    get_config_path,
    get_entries_dir,
    get_topics,
    is_initialized,
    load_config,
    save_config,
)


class TestGetBragDir:
    """Tests for get_brag_dir function."""

    def test_get_brag_dir_success(self, monkeypatch, tmp_path):
        """Get directory when BRAG_DIR is set."""
        brag_dir = tmp_path / "my_brag"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_brag_dir()

        assert result == brag_dir

    def test_get_brag_dir_missing_env(self, monkeypatch):
        """Raise ConfigError when BRAG_DIR not set."""
        monkeypatch.delenv("BRAG_DIR", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            get_brag_dir()

        assert "BRAG_DIR environment variable is not set" in str(exc_info.value)

    def test_get_brag_dir_expansion(self, monkeypatch):
        """Test ~ expansion in paths."""
        monkeypatch.setenv("BRAG_DIR", "~/Documents/brag")

        result = get_brag_dir()

        assert "~" not in str(result)
        assert result == Path.home() / "Documents" / "brag"


class TestGetConfigPath:
    """Tests for get_config_path function."""

    def test_get_config_path(self, monkeypatch, tmp_path):
        """Verify config.yaml path construction."""
        brag_dir = tmp_path / "brag"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_config_path()

        assert result == brag_dir / "config.yaml"


class TestGetEntriesDir:
    """Tests for get_entries_dir function."""

    def test_get_entries_dir(self, monkeypatch, tmp_path):
        """Verify entries/ path construction."""
        brag_dir = tmp_path / "brag"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_entries_dir()

        assert result == brag_dir / "entries"


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_success(self, monkeypatch, tmp_path):
        """Load valid YAML config."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        config_data = {"topics": ["Project Alpha", "Code Review"]}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = load_config()

        assert result == config_data
        assert result["topics"] == ["Project Alpha", "Code Review"]

    def test_load_config_missing_file(self, monkeypatch, tmp_path):
        """Raise ConfigError for missing config."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        with pytest.raises(ConfigError) as exc_info:
            load_config()

        assert "Configuration file not found" in str(exc_info.value)

    def test_load_config_empty_file(self, monkeypatch, tmp_path):
        """Handle empty config file (return empty dict)."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        config_path.touch()  # Create empty file
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = load_config()

        assert result == {}


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_config(self, monkeypatch, tmp_path):
        """Save config and verify file contents."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        config_data = {"topics": ["Project Alpha", "Code Review"]}
        save_config(config_data)

        with open(config_path) as f:
            saved_data = yaml.safe_load(f)

        assert saved_data == config_data

    def test_save_config_overwrites_existing(self, monkeypatch, tmp_path):
        """Save config overwrites existing file."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"topics": ["Old Topic"]}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        new_config = {"topics": ["New Topic"]}
        save_config(new_config)

        with open(config_path) as f:
            saved_data = yaml.safe_load(f)

        assert saved_data == new_config


class TestGetTopics:
    """Tests for get_topics function."""

    def test_get_topics_with_topics(self, monkeypatch, tmp_path):
        """Return list of topics."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"topics": ["Project Alpha", "Code Review"]}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_topics()

        assert result == ["Project Alpha", "Code Review"]

    def test_get_topics_empty(self, monkeypatch, tmp_path):
        """Return empty list when no topics."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"topics": []}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_topics()

        assert result == []

    def test_get_topics_missing_key(self, monkeypatch, tmp_path):
        """Return empty list when topics key is missing."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_topics()

        assert result == []


class TestAddTopic:
    """Tests for add_topic function."""

    def test_add_topic_success(self, monkeypatch, tmp_path):
        """Add new topic to config."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"topics": ["Existing Topic"]}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        add_topic("New Topic")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "New Topic" in config["topics"]
        assert "Existing Topic" in config["topics"]

    def test_add_topic_duplicate(self, monkeypatch, tmp_path):
        """Raise ConfigError for duplicate topic."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"topics": ["Existing Topic"]}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        with pytest.raises(ConfigError) as exc_info:
            add_topic("Existing Topic")

        assert "already exists" in str(exc_info.value)

    def test_add_topic_to_empty_list(self, monkeypatch, tmp_path):
        """Add topic to empty topics list."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"topics": []}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        add_topic("First Topic")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert config["topics"] == ["First Topic"]

    def test_add_topic_missing_topics_key(self, monkeypatch, tmp_path):
        """Add topic when topics key is missing."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        add_topic("New Topic")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert config["topics"] == ["New Topic"]


class TestIsInitialized:
    """Tests for is_initialized function."""

    def test_is_initialized_true(self, monkeypatch, tmp_path):
        """Return True when properly initialized."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        entries_dir = brag_dir / "entries"
        entries_dir.mkdir()
        config_path.touch()
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = is_initialized()

        assert result is True

    def test_is_initialized_false_no_config(self, monkeypatch, tmp_path):
        """Return False without config."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        entries_dir = brag_dir / "entries"
        entries_dir.mkdir()
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = is_initialized()

        assert result is False

    def test_is_initialized_false_no_entries_dir(self, monkeypatch, tmp_path):
        """Return False without entries dir."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        config_path.touch()
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = is_initialized()

        assert result is False

    def test_is_initialized_false_no_env_var(self, monkeypatch):
        """Return False when BRAG_DIR not set."""
        monkeypatch.delenv("BRAG_DIR", raising=False)

        result = is_initialized()

        assert result is False

    def test_is_initialized_false_nonexistent_dir(self, monkeypatch, tmp_path):
        """Return False when brag dir doesn't exist."""
        brag_dir = tmp_path / "nonexistent"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = is_initialized()

        assert result is False

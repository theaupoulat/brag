"""Shared fixtures and test configuration."""

from datetime import date
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from brag.models import Entry


@pytest.fixture
def cli_runner() -> CliRunner:
    """Click CliRunner instance for testing CLI commands."""
    return CliRunner()


@pytest.fixture
def temp_brag_dir(tmp_path: Path) -> Path:
    """Temporary brag directory for testing."""
    brag_dir = tmp_path / "brag"
    brag_dir.mkdir()
    entries_dir = brag_dir / "entries"
    entries_dir.mkdir()
    return brag_dir


@pytest.fixture
def mock_config(temp_brag_dir: Path) -> dict:
    """Mock configuration with sample topics."""
    config = {
        "topics": ["Project Alpha", "Code Review", "Documentation"],
    }
    config_path = temp_brag_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return config


@pytest.fixture
def initialized_brag_dir(temp_brag_dir: Path, mock_config: dict) -> Path:
    """Fully initialized brag directory with config and entries dir."""
    return temp_brag_dir


@pytest.fixture
def sample_entry() -> Entry:
    """Sample Entry object for testing."""
    return Entry(
        title="Implemented user authentication",
        topic="Project Alpha",
        impact="Enabled secure access for 1000+ users",
        tags=["security", "feature"],
        entry_date=date(2024, 11, 25),
    )


@pytest.fixture
def sample_entry_no_tags() -> Entry:
    """Sample Entry without tags."""
    return Entry(
        title="Fixed critical bug",
        topic="Code Review",
        impact="Prevented data loss for customers",
        tags=[],
        entry_date=date(2024, 11, 25),
    )


@pytest.fixture
def sample_entries() -> list[Entry]:
    """List of sample Entry objects for testing."""
    return [
        Entry(
            title="Implemented user authentication",
            topic="Project Alpha",
            impact="Enabled secure access for 1000+ users",
            tags=["security", "feature"],
            entry_date=date(2024, 11, 25),
        ),
        Entry(
            title="Reviewed pull requests",
            topic="Code Review",
            impact="Improved code quality across team",
            tags=["review"],
            entry_date=date(2024, 11, 25),
        ),
        Entry(
            title="Updated API documentation",
            topic="Documentation",
            impact="Reduced support tickets by 20%",
            tags=["docs", "api"],
            entry_date=date(2024, 11, 26),
        ),
    ]


@pytest.fixture
def sample_week_file_content() -> str:
    """Sample week file content for parsing tests."""
    return """# Week 48 - 2024

## 2024-11-25
### Implemented user authentication
- **Topic:** Project Alpha
- **Impact:** Enabled secure access for 1000+ users
- **Tags:** security, feature

### Reviewed pull requests
- **Topic:** Code Review
- **Impact:** Improved code quality across team
- **Tags:** review

## 2024-11-26
### Updated API documentation
- **Topic:** Documentation
- **Impact:** Reduced support tickets by 20%
- **Tags:** docs, api
"""

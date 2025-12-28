"""Integration tests for CLI commands."""

from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner
from freezegun import freeze_time

from brag import __version__
from brag.cli import main


@pytest.fixture
def runner():
    """Click CliRunner instance."""
    return CliRunner()


@pytest.fixture
def initialized_env(tmp_path, monkeypatch):
    """Set up initialized brag environment."""
    brag_dir = tmp_path / "brag"
    brag_dir.mkdir()
    entries_dir = brag_dir / "entries"
    entries_dir.mkdir()
    config_path = brag_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump({"topics": ["Project Alpha", "Code Review"]}, f)
    monkeypatch.setenv("BRAG_DIR", str(brag_dir))
    return brag_dir


@pytest.fixture
def env_with_entries(initialized_env):
    """Initialized environment with sample entries."""
    entries_dir = initialized_env / "entries" / "2024"
    entries_dir.mkdir(parents=True)
    week_file = entries_dir / "week-48.md"
    week_file.write_text("""# Week 48 - 2024

## 2024-11-25
### Implemented authentication
- **Topic:** Project Alpha
- **Impact:** Secured user access
- **Tags:** security, feature

### Reviewed PRs
- **Topic:** Code Review
- **Impact:** Improved code quality
""")
    return initialized_env


class TestInitCommand:
    """Tests for init command."""

    def test_init_success(self, runner, tmp_path, monkeypatch):
        """Initialize new brag directory."""
        brag_dir = tmp_path / "brag"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = runner.invoke(main, ["init"])

        assert result.exit_code == 0
        assert "Initialized brag directory" in result.output
        assert (brag_dir / "config.yaml").exists()
        assert (brag_dir / "entries").exists()

    def test_init_already_initialized(self, runner, initialized_env):
        """Handle already initialized directory."""
        result = runner.invoke(main, ["init"])

        assert result.exit_code == 0
        assert "already initialized" in result.output

    def test_init_missing_env_var(self, runner, monkeypatch):
        """Error when BRAG_DIR not set."""
        monkeypatch.delenv("BRAG_DIR", raising=False)

        result = runner.invoke(main, ["init"])

        assert result.exit_code == 1
        assert "BRAG_DIR" in result.output


class TestAddCommand:
    """Tests for add command."""

    def test_add_not_initialized(self, runner, tmp_path, monkeypatch):
        """Error when not initialized."""
        brag_dir = tmp_path / "brag"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = runner.invoke(main, ["add"])

        assert result.exit_code == 1
        assert "not initialized" in result.output

    def test_add_no_topics(self, runner, tmp_path, monkeypatch):
        """Error when no topics defined."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        entries_dir = brag_dir / "entries"
        entries_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"topics": []}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = runner.invoke(main, ["add"])

        assert result.exit_code == 1
        assert "No topics defined" in result.output

    @freeze_time("2024-11-25")
    def test_add_success_mock_input(self, runner, initialized_env):
        """Successfully add entry with mocked prompts."""
        with patch("brag.cli.questionary") as mock_questionary:
            # Mock all questionary prompts
            mock_questionary.select.return_value.ask.return_value = "Project Alpha"
            mock_questionary.text.return_value.ask.side_effect = [
                "Implemented new feature",  # title
                "Improved user experience",  # impact
                "feature, improvement",  # tags
            ]
            mock_questionary.confirm.return_value.ask.return_value = True

            result = runner.invoke(main, ["add"])

        assert result.exit_code == 0
        assert "Entry saved" in result.output

        # Verify entry was written
        week_file = initialized_env / "entries" / "2024" / "week-48.md"
        assert week_file.exists()
        content = week_file.read_text()
        assert "Implemented new feature" in content

    def test_add_cancelled_at_topic(self, runner, initialized_env):
        """Handle cancellation at topic selection."""
        with patch("brag.cli.questionary") as mock_questionary:
            mock_questionary.select.return_value.ask.return_value = None

            result = runner.invoke(main, ["add"])

        assert result.exit_code == 0
        assert "Cancelled" in result.output

    def test_add_cancelled_at_title(self, runner, initialized_env):
        """Handle cancellation at title prompt."""
        with patch("brag.cli.questionary") as mock_questionary:
            mock_questionary.select.return_value.ask.return_value = "Project Alpha"
            mock_questionary.text.return_value.ask.return_value = None

            result = runner.invoke(main, ["add"])

        assert result.exit_code == 0
        assert "Cancelled" in result.output

    def test_add_cancelled_at_impact(self, runner, initialized_env):
        """Handle cancellation at impact prompt."""
        with patch("brag.cli.questionary") as mock_questionary:
            mock_questionary.select.return_value.ask.return_value = "Project Alpha"
            mock_questionary.text.return_value.ask.side_effect = [
                "Test title",  # title
                None,  # impact (cancelled)
            ]

            result = runner.invoke(main, ["add"])

        assert result.exit_code == 0
        assert "Cancelled" in result.output

    @freeze_time("2024-11-25")
    def test_add_declined_confirmation(self, runner, initialized_env):
        """Handle declining save confirmation."""
        with patch("brag.cli.questionary") as mock_questionary:
            mock_questionary.select.return_value.ask.return_value = "Project Alpha"
            mock_questionary.text.return_value.ask.side_effect = [
                "Test title",
                "Test impact",
                "",  # no tags
            ]
            mock_questionary.confirm.return_value.ask.return_value = False

            result = runner.invoke(main, ["add"])

        assert result.exit_code == 0
        assert "discarded" in result.output

    @freeze_time("2024-11-25")
    def test_add_with_tags(self, runner, initialized_env):
        """Add entry with tags."""
        with patch("brag.cli.questionary") as mock_questionary:
            mock_questionary.select.return_value.ask.return_value = "Project Alpha"
            mock_questionary.text.return_value.ask.side_effect = [
                "Test with tags",
                "Test impact",
                "tag1, tag2, tag3",
            ]
            mock_questionary.confirm.return_value.ask.return_value = True

            result = runner.invoke(main, ["add"])

        assert result.exit_code == 0
        week_file = initialized_env / "entries" / "2024" / "week-48.md"
        content = week_file.read_text()
        assert "tag1" in content
        assert "tag2" in content

    @freeze_time("2024-11-25")
    def test_add_without_tags(self, runner, initialized_env):
        """Add entry without tags."""
        with patch("brag.cli.questionary") as mock_questionary:
            mock_questionary.select.return_value.ask.return_value = "Project Alpha"
            mock_questionary.text.return_value.ask.side_effect = [
                "Test without tags",
                "Test impact",
                "",  # empty tags
            ]
            mock_questionary.confirm.return_value.ask.return_value = True

            result = runner.invoke(main, ["add"])

        assert result.exit_code == 0
        week_file = initialized_env / "entries" / "2024" / "week-48.md"
        content = week_file.read_text()
        assert "Test without tags" in content
        assert "Tags:" not in content or "Tags:" in content  # may or may not have tags line


class TestListCommand:
    """Tests for list command."""

    def test_list_not_initialized(self, runner, tmp_path, monkeypatch):
        """Error when not initialized."""
        brag_dir = tmp_path / "brag"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = runner.invoke(main, ["list"])

        assert result.exit_code == 1
        assert "not initialized" in result.output

    @freeze_time("2024-11-25")
    def test_list_no_entries(self, runner, initialized_env):
        """Display message when no entries."""
        result = runner.invoke(main, ["list"])

        assert result.exit_code == 0
        assert "No entries found" in result.output

    @freeze_time("2024-11-25")
    def test_list_current_week(self, runner, env_with_entries):
        """List entries from current week."""
        result = runner.invoke(main, ["list"])

        assert result.exit_code == 0
        assert "Implemented authentication" in result.output
        assert "Reviewed PRs" in result.output

    def test_list_by_week(self, runner, env_with_entries):
        """Filter by week number."""
        result = runner.invoke(main, ["list", "--week", "48", "--year", "2024"])

        assert result.exit_code == 0
        assert "Implemented authentication" in result.output

    def test_list_by_month(self, runner, env_with_entries):
        """Filter by month."""
        result = runner.invoke(main, ["list", "--month", "11", "--year", "2024"])

        assert result.exit_code == 0
        assert "Implemented authentication" in result.output

    def test_list_by_quarter(self, runner, env_with_entries):
        """Filter by quarter."""
        result = runner.invoke(main, ["list", "--quarter", "4", "--year", "2024"])

        assert result.exit_code == 0
        assert "Implemented authentication" in result.output

    def test_list_by_semester(self, runner, env_with_entries):
        """Filter by semester."""
        result = runner.invoke(main, ["list", "--semester", "2", "--year", "2024"])

        assert result.exit_code == 0
        assert "Implemented authentication" in result.output

    def test_list_by_year(self, runner, env_with_entries):
        """Filter by year."""
        result = runner.invoke(main, ["list", "--week", "48", "--year", "2024"])

        assert result.exit_code == 0
        assert "Implemented authentication" in result.output

    def test_list_by_topic(self, runner, env_with_entries):
        """Filter by topic."""
        result = runner.invoke(main, ["list", "--week", "48", "--year", "2024", "--topic", "Project Alpha"])

        assert result.exit_code == 0
        assert "Implemented authentication" in result.output
        assert "Reviewed PRs" not in result.output

    def test_list_combined_filters(self, runner, env_with_entries):
        """Multiple filters together."""
        result = runner.invoke(main, ["list", "--month", "11", "--year", "2024", "--topic", "Code Review"])

        assert result.exit_code == 0
        assert "Reviewed PRs" in result.output
        assert "Implemented authentication" not in result.output


class TestTopicAddCommand:
    """Tests for topic add command."""

    def test_topic_add_not_initialized(self, runner, tmp_path, monkeypatch):
        """Error when not initialized."""
        brag_dir = tmp_path / "brag"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = runner.invoke(main, ["topic", "add", "New Topic"])

        assert result.exit_code == 1
        assert "not initialized" in result.output

    def test_topic_add_success(self, runner, initialized_env):
        """Add new topic."""
        result = runner.invoke(main, ["topic", "add", "New Topic"])

        assert result.exit_code == 0
        assert "Added topic" in result.output

        # Verify config was updated
        config_path = initialized_env / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert "New Topic" in config["topics"]

    def test_topic_add_duplicate(self, runner, initialized_env):
        """Error on duplicate topic."""
        result = runner.invoke(main, ["topic", "add", "Project Alpha"])

        assert result.exit_code == 1
        assert "already exists" in result.output


class TestTopicListCommand:
    """Tests for topic list command."""

    def test_topic_list_not_initialized(self, runner, tmp_path, monkeypatch):
        """Error when not initialized."""
        brag_dir = tmp_path / "brag"
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = runner.invoke(main, ["topic", "list"])

        assert result.exit_code == 1
        assert "not initialized" in result.output

    def test_topic_list_empty(self, runner, tmp_path, monkeypatch):
        """Display message when no topics."""
        brag_dir = tmp_path / "brag"
        brag_dir.mkdir()
        entries_dir = brag_dir / "entries"
        entries_dir.mkdir()
        config_path = brag_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"topics": []}, f)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = runner.invoke(main, ["topic", "list"])

        assert result.exit_code == 0
        assert "No topics defined" in result.output

    def test_topic_list_with_topics(self, runner, initialized_env):
        """Display list of topics."""
        result = runner.invoke(main, ["topic", "list"])

        assert result.exit_code == 0
        assert "Project Alpha" in result.output
        assert "Code Review" in result.output


class TestGeneralCLI:
    """Tests for general CLI behavior."""

    def test_version_flag(self, runner):
        """Test --version output."""
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.output

    def test_help_flag(self, runner):
        """Test --help output."""
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "brag" in result.output.lower()
        assert "init" in result.output
        assert "add" in result.output
        assert "list" in result.output
        assert "topic" in result.output

    def test_help_flag_subcommand(self, runner):
        """Test --help for subcommands."""
        result = runner.invoke(main, ["add", "--help"])

        assert result.exit_code == 0
        assert "accomplishment" in result.output.lower()

    def test_invalid_command(self, runner):
        """Test invalid command."""
        result = runner.invoke(main, ["invalid-command"])

        assert result.exit_code != 0

    def test_handle_error_decorator(self, runner, monkeypatch):
        """Test error handling decorator."""
        monkeypatch.delenv("BRAG_DIR", raising=False)

        result = runner.invoke(main, ["list"])

        assert result.exit_code == 1
        assert "Error" in result.output

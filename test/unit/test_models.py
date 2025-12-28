"""Unit tests for Entry model."""

from datetime import date

import pytest

from brag.models import Entry


class TestEntryCreation:
    """Tests for Entry creation and initialization."""

    def test_entry_creation(self):
        """Test creating Entry with all fields."""
        entry = Entry(
            title="Implemented feature X",
            topic="Project Alpha",
            impact="Increased user engagement by 25%",
            tags=["feature", "engagement"],
            entry_date=date(2024, 11, 25),
        )

        assert entry.title == "Implemented feature X"
        assert entry.topic == "Project Alpha"
        assert entry.impact == "Increased user engagement by 25%"
        assert entry.tags == ["feature", "engagement"]
        assert entry.entry_date == date(2024, 11, 25)

    def test_entry_creation_with_defaults(self):
        """Test default values for optional fields."""
        entry = Entry(
            title="Fixed bug",
            topic="Maintenance",
            impact="Resolved customer complaint",
        )

        assert entry.title == "Fixed bug"
        assert entry.topic == "Maintenance"
        assert entry.impact == "Resolved customer complaint"
        assert entry.tags == []
        assert entry.entry_date == date.today()

    def test_entry_creation_empty_tags(self):
        """Test Entry with explicitly empty tags list."""
        entry = Entry(
            title="Test entry",
            topic="Testing",
            impact="Test impact",
            tags=[],
            entry_date=date(2024, 11, 25),
        )

        assert entry.tags == []

    def test_entry_creation_with_special_characters(self):
        """Test Entry with special characters in fields."""
        entry = Entry(
            title="Fixed \"quoted\" issue & special <chars>",
            topic="Code Review",
            impact="Resolved 100% of edge cases",
            tags=["special-chars", "test_case"],
            entry_date=date(2024, 11, 25),
        )

        assert '"quoted"' in entry.title
        assert "&" in entry.title
        assert "<chars>" in entry.title


class TestEntryToMarkdown:
    """Tests for Entry.to_markdown() method."""

    def test_entry_to_markdown(self):
        """Test markdown conversion with all fields."""
        entry = Entry(
            title="Implemented user authentication",
            topic="Project Alpha",
            impact="Enabled secure access for 1000+ users",
            tags=["security", "feature"],
            entry_date=date(2024, 11, 25),
        )

        markdown = entry.to_markdown()

        assert "### Implemented user authentication" in markdown
        assert "- **Topic:** Project Alpha" in markdown
        assert "- **Impact:** Enabled secure access for 1000+ users" in markdown
        assert "- **Tags:** security, feature" in markdown

    def test_entry_to_markdown_without_tags(self):
        """Test markdown conversion without tags."""
        entry = Entry(
            title="Fixed critical bug",
            topic="Maintenance",
            impact="Prevented data loss",
            tags=[],
            entry_date=date(2024, 11, 25),
        )

        markdown = entry.to_markdown()

        assert "### Fixed critical bug" in markdown
        assert "- **Topic:** Maintenance" in markdown
        assert "- **Impact:** Prevented data loss" in markdown
        assert "Tags" not in markdown

    def test_entry_to_markdown_single_tag(self):
        """Test markdown conversion with single tag."""
        entry = Entry(
            title="Test entry",
            topic="Testing",
            impact="Test impact",
            tags=["single"],
            entry_date=date(2024, 11, 25),
        )

        markdown = entry.to_markdown()

        assert "- **Tags:** single" in markdown

    def test_entry_to_markdown_preserves_order(self):
        """Test that markdown fields are in correct order."""
        entry = Entry(
            title="Test",
            topic="Topic",
            impact="Impact",
            tags=["tag1", "tag2"],
            entry_date=date(2024, 11, 25),
        )

        markdown = entry.to_markdown()
        lines = markdown.split("\n")

        assert lines[0].startswith("### ")
        assert lines[1].startswith("- **Topic:**")
        assert lines[2].startswith("- **Impact:**")
        assert lines[3].startswith("- **Tags:**")


class TestEntryFromMarkdown:
    """Tests for Entry.from_markdown() class method."""

    def test_entry_from_markdown_complete(self):
        """Parse complete entry from markdown."""
        markdown = """### Implemented user authentication
- **Topic:** Project Alpha
- **Impact:** Enabled secure access for 1000+ users
- **Tags:** security, feature"""

        entry = Entry.from_markdown(markdown, date(2024, 11, 25))

        assert entry is not None
        assert entry.title == "Implemented user authentication"
        assert entry.topic == "Project Alpha"
        assert entry.impact == "Enabled secure access for 1000+ users"
        assert entry.tags == ["security", "feature"]
        assert entry.entry_date == date(2024, 11, 25)

    def test_entry_from_markdown_minimal(self):
        """Parse minimal entry (no tags)."""
        markdown = """### Fixed critical bug
- **Topic:** Code Review
- **Impact:** Prevented data loss for customers"""

        entry = Entry.from_markdown(markdown, date(2024, 11, 25))

        assert entry is not None
        assert entry.title == "Fixed critical bug"
        assert entry.topic == "Code Review"
        assert entry.impact == "Prevented data loss for customers"
        assert entry.tags == []

    def test_entry_from_markdown_invalid(self):
        """Return None for invalid markdown."""
        markdown = """This is not a valid entry format
It has no proper headers or fields"""

        entry = Entry.from_markdown(markdown, date(2024, 11, 25))

        assert entry is None

    def test_entry_from_markdown_missing_title(self):
        """Handle missing title gracefully."""
        markdown = """- **Topic:** Project Alpha
- **Impact:** This entry has no title"""

        entry = Entry.from_markdown(markdown, date(2024, 11, 25))

        assert entry is None

    def test_entry_from_markdown_empty_string(self):
        """Handle empty string."""
        entry = Entry.from_markdown("", date(2024, 11, 25))

        assert entry is None

    def test_entry_from_markdown_whitespace_only(self):
        """Handle whitespace-only string."""
        entry = Entry.from_markdown("   \n\n   ", date(2024, 11, 25))

        assert entry is None

    def test_entry_from_markdown_extra_whitespace(self):
        """Parse entry with extra whitespace."""
        markdown = """### Test entry
- **Topic:**   Test Topic
- **Impact:**   Test impact
- **Tags:**   tag1  ,  tag2  """

        entry = Entry.from_markdown(markdown, date(2024, 11, 25))

        assert entry is not None
        assert entry.title == "Test entry"
        assert entry.topic == "Test Topic"
        assert entry.impact == "Test impact"
        assert entry.tags == ["tag1", "tag2"]


class TestEntryRoundTrip:
    """Tests for to_markdown -> from_markdown round trip."""

    def test_entry_round_trip(self):
        """to_markdown -> from_markdown preserves data."""
        original = Entry(
            title="Implemented user authentication",
            topic="Project Alpha",
            impact="Enabled secure access for 1000+ users",
            tags=["security", "feature"],
            entry_date=date(2024, 11, 25),
        )

        markdown = original.to_markdown()
        parsed = Entry.from_markdown(markdown, original.entry_date)

        assert parsed is not None
        assert parsed.title == original.title
        assert parsed.topic == original.topic
        assert parsed.impact == original.impact
        assert parsed.tags == original.tags
        assert parsed.entry_date == original.entry_date

    def test_entry_round_trip_no_tags(self):
        """Round trip preserves entry without tags."""
        original = Entry(
            title="Fixed bug",
            topic="Maintenance",
            impact="Bug fixed",
            tags=[],
            entry_date=date(2024, 11, 25),
        )

        markdown = original.to_markdown()
        parsed = Entry.from_markdown(markdown, original.entry_date)

        assert parsed is not None
        assert parsed.title == original.title
        assert parsed.tags == []

    @pytest.mark.parametrize(
        "title,topic,impact,tags",
        [
            ("Simple title", "Topic", "Impact", []),
            ("Title with numbers 123", "Topic 2", "Impact 100%", ["tag1"]),
            ("Multi word title here", "Complex Topic Name", "Very long impact description here", ["a", "b", "c"]),
            ("Special chars: & < > \"", "Topic", "Impact", ["special-tag"]),
        ],
    )
    def test_entry_round_trip_parametrized(self, title, topic, impact, tags):
        """Round trip with various input combinations."""
        original = Entry(
            title=title,
            topic=topic,
            impact=impact,
            tags=tags,
            entry_date=date(2024, 11, 25),
        )

        markdown = original.to_markdown()
        parsed = Entry.from_markdown(markdown, original.entry_date)

        assert parsed is not None
        assert parsed.title == original.title
        assert parsed.topic == original.topic
        assert parsed.impact == original.impact
        assert parsed.tags == original.tags

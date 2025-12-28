"""Unit tests for storage operations."""

from datetime import date

import pytest
from freezegun import freeze_time

from brag.models import Entry
from brag.storage import (
    _get_weeks_for_month,
    add_entry,
    ensure_week_file,
    get_entries_filtered,
    get_entries_for_week,
    get_week_file_path,
    get_week_number,
    get_weeks_in_range,
    parse_week_file,
)


class TestGetWeekNumber:
    """Tests for get_week_number function."""

    def test_get_week_number(self):
        """Verify ISO week calculation for various dates."""
        # November 25, 2024 is in week 48
        assert get_week_number(date(2024, 11, 25)) == 48

    def test_get_week_number_january_first(self):
        """Test week number for January 1st."""
        # January 1, 2024 is a Monday, week 1
        assert get_week_number(date(2024, 1, 1)) == 1

    def test_get_week_number_december_31(self):
        """Test week number for December 31st."""
        # December 31, 2024 is in week 1 of 2025 (ISO week)
        assert get_week_number(date(2024, 12, 31)) == 1

    @pytest.mark.parametrize(
        "test_date,expected_week",
        [
            (date(2024, 1, 1), 1),
            (date(2024, 3, 15), 11),
            (date(2024, 6, 30), 26),
            (date(2024, 9, 1), 35),
            (date(2024, 11, 25), 48),
        ],
    )
    def test_get_week_number_parametrized(self, test_date, expected_week):
        """Test week number calculation for various dates."""
        assert get_week_number(test_date) == expected_week


class TestGetWeekFilePath:
    """Tests for get_week_file_path function."""

    def test_get_week_file_path(self, monkeypatch, tmp_path):
        """Test path construction for week files."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        entries_dir.mkdir(parents=True)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_week_file_path(2024, 48)

        assert result == entries_dir / "2024" / "week-48.md"

    def test_get_week_file_path_single_digit_week(self, monkeypatch, tmp_path):
        """Test path with single digit week (should be zero-padded)."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        entries_dir.mkdir(parents=True)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_week_file_path(2024, 1)

        assert result == entries_dir / "2024" / "week-01.md"


class TestEnsureWeekFile:
    """Tests for ensure_week_file function."""

    def test_ensure_week_file_creates_new(self, monkeypatch, tmp_path):
        """Create new week file with header."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        entries_dir.mkdir(parents=True)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = ensure_week_file(2024, 48)

        assert result.exists()
        content = result.read_text()
        assert "# Week 48 - 2024" in content

    def test_ensure_week_file_existing(self, monkeypatch, tmp_path):
        """Don't overwrite existing file."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        week_file = year_dir / "week-48.md"
        original_content = "# Existing content\n"
        week_file.write_text(original_content)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = ensure_week_file(2024, 48)

        assert result.read_text() == original_content

    def test_ensure_week_file_creates_directory(self, monkeypatch, tmp_path):
        """Create year directory if needed."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        entries_dir.mkdir(parents=True)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = ensure_week_file(2024, 48)

        assert result.parent.exists()
        assert result.parent.name == "2024"


class TestAddEntry:
    """Tests for add_entry function."""

    def test_add_entry_new_file(self, monkeypatch, tmp_path):
        """Add entry to new week file."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        entries_dir.mkdir(parents=True)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        entry = Entry(
            title="Test entry",
            topic="Project Alpha",
            impact="Test impact",
            tags=["tag1"],
            entry_date=date(2024, 11, 25),
        )

        add_entry(entry)

        week_file = entries_dir / "2024" / "week-48.md"
        content = week_file.read_text()
        assert "### Test entry" in content
        assert "- **Topic:** Project Alpha" in content
        assert "## 2024-11-25" in content

    def test_add_entry_existing_file(self, monkeypatch, tmp_path):
        """Append to existing week file."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        week_file = year_dir / "week-48.md"
        week_file.write_text("# Week 48 - 2024\n\n## 2024-11-25\n### Existing entry\n- **Topic:** Test\n- **Impact:** Test\n")
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        entry = Entry(
            title="New entry",
            topic="Project Alpha",
            impact="Test impact",
            tags=[],
            entry_date=date(2024, 11, 25),
        )

        add_entry(entry)

        content = week_file.read_text()
        assert "### Existing entry" in content
        assert "### New entry" in content

    def test_add_entry_new_date_section(self, monkeypatch, tmp_path):
        """Create new date section in file."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        week_file = year_dir / "week-48.md"
        week_file.write_text("# Week 48 - 2024\n\n## 2024-11-25\n### Existing entry\n- **Topic:** Test\n- **Impact:** Test\n")
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        entry = Entry(
            title="New date entry",
            topic="Project Alpha",
            impact="Test impact",
            tags=[],
            entry_date=date(2024, 11, 26),
        )

        add_entry(entry)

        content = week_file.read_text()
        assert "## 2024-11-25" in content
        assert "## 2024-11-26" in content
        assert "### New date entry" in content


class TestParseWeekFile:
    """Tests for parse_week_file function."""

    def test_parse_week_file_empty(self, tmp_path):
        """Return empty list for non-existent file."""
        file_path = tmp_path / "nonexistent.md"

        result = parse_week_file(file_path)

        assert result == []

    def test_parse_week_file_single_entry(self, tmp_path):
        """Parse file with one entry."""
        file_path = tmp_path / "week-48.md"
        content = """# Week 48 - 2024

## 2024-11-25
### Implemented user authentication
- **Topic:** Project Alpha
- **Impact:** Enabled secure access for 1000+ users
- **Tags:** security, feature
"""
        file_path.write_text(content)

        result = parse_week_file(file_path)

        assert len(result) == 1
        assert result[0].title == "Implemented user authentication"
        assert result[0].topic == "Project Alpha"
        assert result[0].entry_date == date(2024, 11, 25)

    def test_parse_week_file_multiple_entries(self, tmp_path):
        """Parse multiple entries per date."""
        file_path = tmp_path / "week-48.md"
        content = """# Week 48 - 2024

## 2024-11-25
### First entry
- **Topic:** Topic1
- **Impact:** Impact1

### Second entry
- **Topic:** Topic2
- **Impact:** Impact2
"""
        file_path.write_text(content)

        result = parse_week_file(file_path)

        assert len(result) == 2
        assert result[0].title == "First entry"
        assert result[1].title == "Second entry"

    def test_parse_week_file_multiple_dates(self, tmp_path):
        """Parse entries across multiple dates."""
        file_path = tmp_path / "week-48.md"
        content = """# Week 48 - 2024

## 2024-11-25
### Monday entry
- **Topic:** Topic1
- **Impact:** Impact1

## 2024-11-26
### Tuesday entry
- **Topic:** Topic2
- **Impact:** Impact2
"""
        file_path.write_text(content)

        result = parse_week_file(file_path)

        assert len(result) == 2
        assert result[0].entry_date == date(2024, 11, 25)
        assert result[1].entry_date == date(2024, 11, 26)


class TestGetWeeksInRange:
    """Tests for get_weeks_in_range function."""

    def test_get_weeks_in_range(self):
        """Calculate week ranges correctly."""
        result = get_weeks_in_range(2024, 1, 3)

        assert result == [(2024, 1), (2024, 2), (2024, 3)]

    def test_get_weeks_in_range_full_year(self):
        """Get all weeks in a year."""
        result = get_weeks_in_range(2024)

        assert len(result) == 52
        assert result[0] == (2024, 1)
        assert result[-1] == (2024, 52)

    def test_get_weeks_in_range_53_week_year(self):
        """Handle years with 53 weeks."""
        # 2020 has 53 weeks
        result = get_weeks_in_range(2020)

        assert len(result) == 53
        assert result[-1] == (2020, 53)


class TestGetEntriesForWeek:
    """Tests for get_entries_for_week function."""

    def test_get_entries_for_week(self, monkeypatch, tmp_path):
        """Retrieve entries for specific week."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        week_file = year_dir / "week-48.md"
        content = """# Week 48 - 2024

## 2024-11-25
### Test entry
- **Topic:** Topic
- **Impact:** Impact
"""
        week_file.write_text(content)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_entries_for_week(2024, 48)

        assert len(result) == 1
        assert result[0].title == "Test entry"


class TestGetEntriesFiltered:
    """Tests for get_entries_filtered function."""

    @freeze_time("2024-11-25")
    def test_get_entries_filtered_current_week_default(self, monkeypatch, tmp_path):
        """Default to current week."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        week_file = year_dir / "week-48.md"
        content = """# Week 48 - 2024

## 2024-11-25
### Test entry
- **Topic:** Topic
- **Impact:** Impact
"""
        week_file.write_text(content)
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_entries_filtered()

        assert len(result) == 1
        assert result[0].title == "Test entry"

    def test_get_entries_filtered_by_week(self, monkeypatch, tmp_path):
        """Filter by specific week."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        week48 = year_dir / "week-48.md"
        week48.write_text("""# Week 48 - 2024

## 2024-11-25
### Week 48 entry
- **Topic:** Topic
- **Impact:** Impact
""")
        week49 = year_dir / "week-49.md"
        week49.write_text("""# Week 49 - 2024

## 2024-12-02
### Week 49 entry
- **Topic:** Topic
- **Impact:** Impact
""")
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_entries_filtered(year=2024, week=48)

        assert len(result) == 1
        assert result[0].title == "Week 48 entry"

    def test_get_entries_filtered_by_month(self, monkeypatch, tmp_path):
        """Filter by month."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        # November entries (week 44-48)
        week47 = year_dir / "week-47.md"
        week47.write_text("""# Week 47 - 2024

## 2024-11-18
### November entry
- **Topic:** Topic
- **Impact:** Impact
""")
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_entries_filtered(year=2024, month=11)

        assert len(result) == 1
        assert result[0].title == "November entry"

    def test_get_entries_filtered_by_quarter(self, monkeypatch, tmp_path):
        """Filter by quarter (Q1-Q4)."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        # Q4 = October-December (months 10-12)
        week44 = year_dir / "week-44.md"
        week44.write_text("""# Week 44 - 2024

## 2024-10-28
### October entry
- **Topic:** Topic
- **Impact:** Impact
""")
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_entries_filtered(year=2024, quarter=4)

        assert len(result) == 1
        assert result[0].title == "October entry"

    def test_get_entries_filtered_by_semester(self, monkeypatch, tmp_path):
        """Filter by semester (1-2)."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        # Semester 2 = July-December
        week44 = year_dir / "week-44.md"
        week44.write_text("""# Week 44 - 2024

## 2024-10-28
### Second semester entry
- **Topic:** Topic
- **Impact:** Impact
""")
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_entries_filtered(year=2024, semester=2)

        assert len(result) == 1
        assert result[0].title == "Second semester entry"

    def test_get_entries_filtered_by_topic(self, monkeypatch, tmp_path):
        """Filter by topic (case-insensitive)."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        week48 = year_dir / "week-48.md"
        week48.write_text("""# Week 48 - 2024

## 2024-11-25
### Alpha entry
- **Topic:** Project Alpha
- **Impact:** Impact

### Beta entry
- **Topic:** Project Beta
- **Impact:** Impact
""")
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_entries_filtered(year=2024, week=48, topic="project alpha")

        assert len(result) == 1
        assert result[0].title == "Alpha entry"

    def test_get_entries_filtered_combined(self, monkeypatch, tmp_path):
        """Combine multiple filters."""
        brag_dir = tmp_path / "brag"
        entries_dir = brag_dir / "entries"
        year_dir = entries_dir / "2024"
        year_dir.mkdir(parents=True)
        week48 = year_dir / "week-48.md"
        week48.write_text("""# Week 48 - 2024

## 2024-11-25
### Target entry
- **Topic:** Project Alpha
- **Impact:** Impact

### Other entry
- **Topic:** Project Beta
- **Impact:** Impact
""")
        monkeypatch.setenv("BRAG_DIR", str(brag_dir))

        result = get_entries_filtered(year=2024, week=48, topic="Project Alpha")

        assert len(result) == 1
        assert result[0].title == "Target entry"


class TestGetWeeksForMonth:
    """Tests for _get_weeks_for_month function."""

    def test_get_weeks_for_month(self):
        """Get weeks that overlap with month."""
        result = _get_weeks_for_month(2024, 11)

        # November 2024 spans weeks 44-48
        assert (2024, 44) in result
        assert (2024, 48) in result

    def test_get_weeks_for_month_year_boundary(self):
        """Handle December/January edge case."""
        # December 2024 includes week 1 of 2025
        result = _get_weeks_for_month(2024, 12)

        # Check that we have weeks for December
        assert len(result) > 0
        # December 31, 2024 is in ISO week 1 of 2025
        assert (2025, 1) in result

    def test_get_weeks_for_month_january(self):
        """Test January which may include weeks from previous year."""
        result = _get_weeks_for_month(2024, 1)

        assert len(result) > 0
        assert (2024, 1) in result

    @pytest.mark.parametrize(
        "year,month",
        [
            (2024, 1),
            (2024, 6),
            (2024, 12),
            (2020, 2),  # Leap year February
        ],
    )
    def test_get_weeks_for_month_various(self, year, month):
        """Test various months return valid weeks."""
        result = _get_weeks_for_month(year, month)

        assert len(result) > 0
        for y, w in result:
            assert 1 <= w <= 53

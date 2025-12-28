"""Storage operations for brag entries."""

import re
from datetime import date
from pathlib import Path
from typing import Optional

from .config import get_entries_dir
from .models import Entry


def get_week_number(d: date) -> int:
    """Get ISO week number for a date.

    Args:
        d: Date to get week number for.

    Returns:
        ISO week number (1-52/53).
    """
    return d.isocalendar()[1]


def get_week_file_path(year: int, week: int) -> Path:
    """Get the path to a week file.

    Args:
        year: Year.
        week: Week number.

    Returns:
        Path to the week file.
    """
    entries_dir = get_entries_dir()
    return entries_dir / str(year) / f"week-{week:02d}.md"


def ensure_week_file(year: int, week: int) -> Path:
    """Ensure the week file exists, creating it if necessary.

    Args:
        year: Year.
        week: Week number.

    Returns:
        Path to the week file.
    """
    file_path = get_week_file_path(year, week)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        with open(file_path, "w") as f:
            f.write(f"# Week {week} - {year}\n")

    return file_path


def add_entry(entry: Entry) -> None:
    """Add an entry to the appropriate week file.

    Args:
        entry: Entry to add.
    """
    year = entry.entry_date.year
    week = get_week_number(entry.entry_date)
    file_path = ensure_week_file(year, week)

    # Read existing content
    with open(file_path) as f:
        content = f.read()

    # Check if date section exists
    date_header = f"## {entry.entry_date.isoformat()}"
    if date_header not in content:
        content = content.rstrip() + f"\n\n{date_header}\n"

    # Add entry under the date section
    entry_md = entry.to_markdown()
    content = content.rstrip() + f"\n{entry_md}\n"

    # Write back
    with open(file_path, "w") as f:
        f.write(content)


def parse_week_file(file_path: Path) -> list[Entry]:
    """Parse entries from a week file.

    Args:
        file_path: Path to the week file.

    Returns:
        List of entries.
    """
    if not file_path.exists():
        return []

    with open(file_path) as f:
        content = f.read()

    entries: list[Entry] = []
    current_date: Optional[date] = None
    current_entry_lines: list[str] = []

    for line in content.split("\n"):
        # Check for date header
        date_match = re.match(r"^## (\d{4}-\d{2}-\d{2})$", line)
        if date_match:
            # Save previous entry if exists
            if current_entry_lines and current_date:
                entry = Entry.from_markdown(
                    "\n".join(current_entry_lines), current_date
                )
                if entry:
                    entries.append(entry)
                current_entry_lines = []

            current_date = date.fromisoformat(date_match.group(1))
            continue

        # Check for entry header
        if line.startswith("### "):
            # Save previous entry if exists
            if current_entry_lines and current_date:
                entry = Entry.from_markdown(
                    "\n".join(current_entry_lines), current_date
                )
                if entry:
                    entries.append(entry)

            current_entry_lines = [line]
        elif current_entry_lines:
            current_entry_lines.append(line)

    # Don't forget the last entry
    if current_entry_lines and current_date:
        entry = Entry.from_markdown("\n".join(current_entry_lines), current_date)
        if entry:
            entries.append(entry)

    return entries


def get_weeks_in_range(
    year: int,
    start_week: Optional[int] = None,
    end_week: Optional[int] = None,
) -> list[tuple[int, int]]:
    """Get list of (year, week) tuples in a range.

    Args:
        year: Year.
        start_week: Starting week (inclusive).
        end_week: Ending week (inclusive).

    Returns:
        List of (year, week) tuples.
    """
    # Get max week for the year
    from datetime import date as dt

    # Check if the year has 52 or 53 weeks
    dec_28 = dt(year, 12, 28)
    max_week = dec_28.isocalendar()[1]

    start = start_week or 1
    end = end_week or max_week

    return [(year, w) for w in range(start, min(end, max_week) + 1)]


def get_entries_for_week(year: int, week: int) -> list[Entry]:
    """Get all entries for a specific week.

    Args:
        year: Year.
        week: Week number.

    Returns:
        List of entries.
    """
    file_path = get_week_file_path(year, week)
    return parse_week_file(file_path)


def get_entries_filtered(
    year: Optional[int] = None,
    week: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
    semester: Optional[int] = None,
    topic: Optional[str] = None,
) -> list[Entry]:
    """Get entries with optional filters.

    Args:
        year: Filter by year.
        week: Filter by week number.
        month: Filter by month (1-12).
        quarter: Filter by quarter (1-4).
        semester: Filter by semester (1 = Jan-Jun, 2 = Jul-Dec).
        topic: Filter by topic name.

    Returns:
        List of matching entries.
    """
    today = date.today()
    filter_year = year or today.year

    # Determine week range based on filters
    if week is not None:
        # Specific week
        weeks = [(filter_year, week)]
    elif month is not None:
        # Month: find weeks that fall in this month
        weeks = _get_weeks_for_month(filter_year, month)
    elif quarter is not None:
        # Quarter: months 1-3, 4-6, 7-9, 10-12
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        weeks = []
        for m in range(start_month, end_month + 1):
            weeks.extend(_get_weeks_for_month(filter_year, m))
        weeks = list(set(weeks))  # Remove duplicates
    elif semester is not None:
        # Semester: 1 = Jan-Jun, 2 = Jul-Dec
        if semester == 1:
            start_month, end_month = 1, 6
        else:
            start_month, end_month = 7, 12
        weeks = []
        for m in range(start_month, end_month + 1):
            weeks.extend(_get_weeks_for_month(filter_year, m))
        weeks = list(set(weeks))  # Remove duplicates
    else:
        # Default to current week
        weeks = [(today.year, get_week_number(today))]

    # Collect entries from all relevant weeks
    all_entries: list[Entry] = []
    for y, w in sorted(set(weeks)):
        entries = get_entries_for_week(y, w)
        all_entries.extend(entries)

    # Apply date filters for month/quarter/semester
    if month is not None:
        all_entries = [e for e in all_entries if e.entry_date.month == month]
    elif quarter is not None:
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        all_entries = [
            e for e in all_entries if start_month <= e.entry_date.month <= end_month
        ]
    elif semester is not None:
        if semester == 1:
            all_entries = [e for e in all_entries if 1 <= e.entry_date.month <= 6]
        else:
            all_entries = [e for e in all_entries if 7 <= e.entry_date.month <= 12]

    # Filter by topic if specified
    if topic:
        all_entries = [
            e for e in all_entries if e.topic.lower() == topic.lower()
        ]

    # Sort by date
    all_entries.sort(key=lambda e: e.entry_date)

    return all_entries


def _get_weeks_for_month(year: int, month: int) -> list[tuple[int, int]]:
    """Get all weeks that have days in a given month.

    Args:
        year: Year.
        month: Month (1-12).

    Returns:
        List of (year, week) tuples.
    """
    from calendar import monthrange

    _, days_in_month = monthrange(year, month)
    weeks = set()

    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        iso_year, iso_week, _ = d.isocalendar()
        weeks.add((iso_year, iso_week))

    return list(weeks)

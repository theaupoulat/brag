"""Sample test data for brag tests."""

from datetime import date

from brag.models import Entry

# Sample topics list
SAMPLE_TOPICS = ["Project Alpha", "Code Review", "Documentation", "API Performance"]

# Sample configurations
SAMPLE_CONFIG_EMPTY = {"topics": []}

SAMPLE_CONFIG_WITH_TOPICS = {"topics": SAMPLE_TOPICS}

SAMPLE_CONFIG_MINIMAL = {}

# Sample Entry objects
SAMPLE_ENTRY_COMPLETE = Entry(
    title="Implemented user authentication",
    topic="Project Alpha",
    impact="Enabled secure access for 1000+ users",
    tags=["security", "feature"],
    entry_date=date(2024, 11, 25),
)

SAMPLE_ENTRY_NO_TAGS = Entry(
    title="Fixed critical bug",
    topic="Code Review",
    impact="Prevented data loss for customers",
    tags=[],
    entry_date=date(2024, 11, 25),
)

SAMPLE_ENTRY_MULTILINE = Entry(
    title="Optimized database queries",
    topic="API Performance",
    impact="Reduced response time from 500ms to 50ms. Improved user experience significantly.",
    tags=["performance", "database"],
    entry_date=date(2024, 11, 26),
)

# Sample markdown strings
SAMPLE_MARKDOWN_COMPLETE = """### Implemented user authentication
- **Topic:** Project Alpha
- **Impact:** Enabled secure access for 1000+ users
- **Tags:** security, feature"""

SAMPLE_MARKDOWN_NO_TAGS = """### Fixed critical bug
- **Topic:** Code Review
- **Impact:** Prevented data loss for customers"""

SAMPLE_MARKDOWN_INVALID = """This is not a valid entry format
It has no proper headers or fields"""

SAMPLE_MARKDOWN_MISSING_TITLE = """- **Topic:** Project Alpha
- **Impact:** This entry has no title"""

SAMPLE_MARKDOWN_MINIMAL = """### Just a title"""

# Sample week file contents
SAMPLE_WEEK_FILE_SINGLE_ENTRY = """# Week 48 - 2024

## 2024-11-25
### Implemented user authentication
- **Topic:** Project Alpha
- **Impact:** Enabled secure access for 1000+ users
- **Tags:** security, feature
"""

SAMPLE_WEEK_FILE_MULTIPLE_ENTRIES = """# Week 48 - 2024

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

SAMPLE_WEEK_FILE_EMPTY = """# Week 48 - 2024
"""

# Date-related test data
DATES_IN_WEEK_48_2024 = [
    date(2024, 11, 25),  # Monday
    date(2024, 11, 26),  # Tuesday
    date(2024, 11, 27),  # Wednesday
    date(2024, 11, 28),  # Thursday
    date(2024, 11, 29),  # Friday
    date(2024, 11, 30),  # Saturday
    date(2024, 12, 1),   # Sunday
]

# Years with 53 weeks (for edge case testing)
YEARS_WITH_53_WEEKS = [2020, 2026, 2032]

# Month boundary dates for testing
MONTH_BOUNDARY_DATES = {
    "january_start": date(2024, 1, 1),
    "january_end": date(2024, 1, 31),
    "december_start": date(2024, 12, 1),
    "december_end": date(2024, 12, 31),
    "leap_year_feb": date(2024, 2, 29),
}

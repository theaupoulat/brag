"""Data models for brag entries."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Entry:
    """Represents a single brag entry."""

    title: str
    topic: str
    impact: str
    tags: list[str] = field(default_factory=list)
    entry_date: date = field(default_factory=date.today)

    def to_markdown(self) -> str:
        """Convert entry to markdown format.

        Returns:
            Markdown formatted string.
        """
        lines = [
            f"### {self.title}",
            f"- **Topic:** {self.topic}",
            f"- **Impact:** {self.impact}",
        ]
        if self.tags:
            lines.append(f"- **Tags:** {', '.join(self.tags)}")
        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, markdown: str, entry_date: date) -> Optional["Entry"]:
        """Parse an entry from markdown.

        Args:
            markdown: Markdown string representing an entry.
            entry_date: Date of the entry.

        Returns:
            Entry object or None if parsing fails.
        """
        lines = markdown.strip().split("\n")
        if not lines:
            return None

        title = ""
        topic = ""
        impact = ""
        tags: list[str] = []

        for line in lines:
            line = line.strip()
            if line.startswith("### "):
                title = line[4:].strip()
            elif line.startswith("- **Topic:**"):
                topic = line.replace("- **Topic:**", "").strip()
            elif line.startswith("- **Impact:**"):
                impact = line.replace("- **Impact:**", "").strip()
            elif line.startswith("- **Tags:**"):
                tags_str = line.replace("- **Tags:**", "").strip()
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        if not title:
            return None

        return cls(
            title=title,
            topic=topic,
            impact=impact,
            tags=tags,
            entry_date=entry_date,
        )

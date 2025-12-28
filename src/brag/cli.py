"""CLI commands for brag."""

import functools
import sys
from datetime import date

import click
import questionary
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from . import __version__
from .config import (
    ConfigError,
    add_topic,
    get_brag_dir,
    get_config_path,
    get_entries_dir,
    get_topics,
    is_initialized,
    save_config,
)
from .models import Entry
from .storage import get_entries_filtered, get_week_number, add_entry as storage_add_entry

console = Console()


def handle_error(func):
    """Decorator to handle common errors."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConfigError as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled.[/yellow]")
            sys.exit(0)

    return wrapper


@click.group()
@click.version_option(version=__version__, prog_name="brag")
def main():
    """Brag - Track your work accomplishments and build your brag document.

    Set BRAG_DIR environment variable to specify where your brag documents are stored.

    \b
    Example:
      export BRAG_DIR=~/Documents/brag
      brag init
      brag add
    """
    pass


@main.command()
@handle_error
def init():
    """Initialize a new brag document directory.

    Creates the necessary directory structure and configuration file.

    \b
    Structure created:
      $BRAG_DIR/
      ├── config.yaml     # Configuration and topics
      └── entries/        # Weekly entry files
    """
    try:
        brag_dir = get_brag_dir()
    except ConfigError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if is_initialized():
        console.print(
            f"[yellow]Brag directory already initialized at:[/yellow] {brag_dir}"
        )
        return

    # Create directories
    brag_dir.mkdir(parents=True, exist_ok=True)
    entries_dir = get_entries_dir()
    entries_dir.mkdir(parents=True, exist_ok=True)

    # Create config file
    config_path = get_config_path()
    initial_config = {
        "topics": [],
    }
    save_config(initial_config)

    console.print(f"[green]✓[/green] Initialized brag directory at: {brag_dir}")
    console.print(f"  [dim]Created:[/dim] {config_path}")
    console.print(f"  [dim]Created:[/dim] {entries_dir}/")
    console.print()
    console.print("[dim]Next steps:[/dim]")
    console.print("  1. Add a topic: [cyan]brag topic add \"Your Topic\"[/cyan]")
    console.print("  2. Add an entry: [cyan]brag add[/cyan]")


@main.command("add")
@handle_error
def add_entry_cmd():
    """Add a new accomplishment entry (interactive).

    Prompts you to select a topic, describe what you did, and note the impact.

    \b
    Steps:
      1. Select a topic from your defined topics
      2. Describe what you did (supports multi-line)
      3. Describe the impact (who benefited, metrics, etc.)
      4. Add optional tags
      5. Preview and confirm
    """
    if not is_initialized():
        console.print(
            "[red]Error:[/red] Brag directory not initialized.\n"
            "Run [cyan]brag init[/cyan] first."
        )
        sys.exit(1)

    topics = get_topics()
    if not topics:
        console.print(
            "[red]Error:[/red] No topics defined yet.\n"
            "Add a topic first: [cyan]brag topic add \"Your Topic\"[/cyan]"
        )
        sys.exit(1)

    # Select topic
    topic = questionary.select(
        "Select a topic:",
        choices=topics,
        use_shortcuts=True,
    ).ask()

    if topic is None:
        console.print("[yellow]Cancelled.[/yellow]")
        return

    # What did you do?
    title = questionary.text(
        "What did you do?\n",
        multiline=True,
        instruction="(Press Meta+Enter or Esc then Enter to submit)",
    ).ask()

    if not title or not title.strip():
        console.print("[yellow]Cancelled.[/yellow]")
        return

    title = title.strip()

    # What was the impact?
    impact = questionary.text(
        "What was the impact? (Who benefited? What changed? Any metrics?)\n",
        multiline=True,
        instruction="(Press Meta+Enter or Esc then Enter to submit)",
    ).ask()

    if not impact or not impact.strip():
        console.print("[yellow]Cancelled.[/yellow]")
        return

    impact = impact.strip()

    # Tags (optional)
    tags_input = questionary.text(
        "Tags? (optional, comma-separated)\n",
    ).ask()

    tags = []
    if tags_input:
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

    # Create entry
    entry = Entry(
        title=title,
        topic=topic,
        impact=impact,
        tags=tags,
        entry_date=date.today(),
    )

    # Preview
    console.print()
    console.print(Panel(Markdown(entry.to_markdown()), title="Preview", border_style="blue"))
    console.print()

    # Confirm
    confirm = questionary.confirm("Save this entry?", default=True).ask()

    if confirm:
        storage_add_entry(entry)
        week = get_week_number(entry.entry_date)
        console.print(
            f"[green]✓[/green] Entry saved to week {week} ({entry.entry_date.isoformat()})"
        )
    else:
        console.print("[yellow]Entry discarded.[/yellow]")


@main.command("list")
@click.option("--week", type=int, help="Filter by week number (1-52).")
@click.option("--month", type=int, help="Filter by month (1-12).")
@click.option("--quarter", type=int, help="Filter by quarter (1-4).")
@click.option(
    "--semester",
    type=int,
    help="Filter by semester (1 = Jan-Jun, 2 = Jul-Dec).",
)
@click.option(
    "--year",
    type=int,
    help="Filter by year (defaults to current year).",
)
@click.option("--topic", type=str, help="Filter by topic name.")
@handle_error
def list_entries(week, month, quarter, semester, year, topic):
    """List entries with optional filters.

    By default, shows entries from the current week. Filters can be combined.

    \b
    Examples:
      brag list                      # Current week
      brag list --month 11           # All of November
      brag list --quarter 4 --year 2024
      brag list --topic "API performance"
    """
    if not is_initialized():
        console.print(
            "[red]Error:[/red] Brag directory not initialized.\n"
            "Run [cyan]brag init[/cyan] first."
        )
        sys.exit(1)

    entries = get_entries_filtered(
        year=year,
        week=week,
        month=month,
        quarter=quarter,
        semester=semester,
        topic=topic,
    )

    if not entries:
        console.print("[yellow]No entries found for the specified filters.[/yellow]")
        return

    # Build filter description
    filter_parts = []
    if week:
        filter_parts.append(f"Week {week}")
    if month:
        filter_parts.append(f"Month {month}")
    if quarter:
        filter_parts.append(f"Q{quarter}")
    if semester:
        filter_parts.append(f"Semester {semester}")
    if year:
        filter_parts.append(str(year))
    if topic:
        filter_parts.append(f"Topic: {topic}")

    if not filter_parts:
        today = date.today()
        filter_parts.append(f"Week {get_week_number(today)}, {today.year}")

    filter_desc = " | ".join(filter_parts)

    console.print()
    console.print(f"[bold]Entries[/bold] ({filter_desc})")
    console.print()

    # Group by date
    entries_by_date: dict[date, list[Entry]] = {}
    for entry in entries:
        if entry.entry_date not in entries_by_date:
            entries_by_date[entry.entry_date] = []
        entries_by_date[entry.entry_date].append(entry)

    for entry_date in sorted(entries_by_date.keys()):
        console.print(f"[bold blue]## {entry_date.isoformat()}[/bold blue]")
        for entry in entries_by_date[entry_date]:
            console.print(Markdown(entry.to_markdown()))
            console.print()


@main.group()
def topic():
    """Manage topics for your accomplishments.

    Topics help categorize your accomplishments for easier filtering and organization.

    \b
    Commands:
      add   - Add a new topic
      list  - List all defined topics
    """
    pass


@topic.command("add")
@click.argument("name")
@handle_error
def topic_add(name):
    """Add a new topic.

    \b
    Arguments:
      NAME  The name of the topic to add

    \b
    Example:
      brag topic add "Q1 Objectives"
      brag topic add "Improve API performance"
    """
    if not is_initialized():
        console.print(
            "[red]Error:[/red] Brag directory not initialized.\n"
            "Run [cyan]brag init[/cyan] first."
        )
        sys.exit(1)

    try:
        add_topic(name)
        console.print(f"[green]✓[/green] Added topic: {name}")
    except ConfigError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@topic.command("list")
@handle_error
def topic_list():
    """List all defined topics.

    Shows all topics that have been added to your configuration.
    """
    if not is_initialized():
        console.print(
            "[red]Error:[/red] Brag directory not initialized.\n"
            "Run [cyan]brag init[/cyan] first."
        )
        sys.exit(1)

    topics = get_topics()

    if not topics:
        console.print("[yellow]No topics defined yet.[/yellow]")
        console.print("Add a topic: [cyan]brag topic add \"Your Topic\"[/cyan]")
        return

    console.print("[bold]Topics:[/bold]")
    for topic in topics:
        console.print(f"  • {topic}")


if __name__ == "__main__":
    main()

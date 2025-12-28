# Brag

A CLI tool to track your work accomplishments and build your brag document.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

**New to brag documents?** See [howto.md](howto.md) for tips on writing effective brag documents.

The brag document concept was popularized by Julia Evans. Read her excellent blog post: [Get your work recognized: write a brag document](https://jvns.ca/blog/brag-documents/).

## Features

- **Simple CLI interface** - Add entries quickly from the terminal
- **Interactive prompts** - Guided entry creation with topic selection
- **Organized by week** - Entries stored in weekly Markdown files
- **Flexible filtering** - View entries by week, month, quarter, semester, or topic
- **Human-readable format** - All data stored as Markdown, easy to read and edit
- **Topic management** - Organize accomplishments by project or goal

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Install with uv

```bash
# Clone the repository
git clone https://github.com/yourusername/brag.git
cd brag

# Install the package
uv pip install .

# Or for development (editable install)
uv pip install -e .
```

### Run without installing

```bash
# Run directly during development
uv run brag --help
```

## Quick Start

```bash
# 1. Set your brag directory (add to your shell profile)
export BRAG_DIR=~/Documents/brag

# 2. Initialize the directory structure
brag init

# 3. Add your first topic
brag topic add "Q1 Objectives"

# 4. Add an accomplishment
brag add

# 5. View your entries
brag list
```

## Configuration

### Environment Variable

Set `BRAG_DIR` to specify where your brag documents are stored:

```bash
# Add to ~/.bashrc, ~/.zshrc, or your shell profile
export BRAG_DIR=~/Documents/brag
```

### Directory Structure

```
$BRAG_DIR/
├── config.yaml          # Topics and configuration
└── entries/
    └── 2024/
        ├── week-48.md   # Entries for week 48
        └── week-49.md   # Entries for week 49
```

### Configuration File

The `config.yaml` file stores your topics:

```yaml
topics:
  - Q1 Objectives
  - Improve API performance
  - Team leadership
  - Technical debt reduction
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `brag init` | Initialize a new brag document directory |
| `brag add` | Add a new accomplishment (interactive) |
| `brag list` | List entries with optional filters |
| `brag topic add "Name"` | Add a new topic |
| `brag topic list` | List all defined topics |

Use `brag --help` or `brag <command> --help` for detailed information about each command.

### brag init

Creates the directory structure and configuration file.

```bash
brag init
```

### brag add

Interactive prompt to add a new entry:

```bash
brag add
```

You'll be prompted to:
1. Select a topic from your list
2. Describe what you did (supports multi-line input)
3. Describe the impact (who benefited, metrics, etc.)
4. Add optional tags
5. Preview and confirm

### brag list

View entries with optional filters:

```bash
# Current week (default)
brag list

# Specific week
brag list --week 48

# Entire month
brag list --month 11

# Quarter
brag list --quarter 4

# Semester (1 = Jan-Jun, 2 = Jul-Dec)
brag list --semester 2

# Specific year
brag list --year 2024

# Filter by topic
brag list --topic "API performance"

# Combine filters
brag list --quarter 4 --year 2024 --topic "Q1 Objectives"
```

### brag topic

Manage your topics:

```bash
# Add a new topic
brag topic add "New Project Initiative"

# List all topics
brag topic list
```

## File Format

Entries are stored as Markdown files organized by week:

```markdown
# Week 48 - 2024

## 2024-11-25
### Reduced API latency by 40%
- **Topic:** Improve API performance
- **Impact:** Faster response times improved user satisfaction scores
- **Tags:** backend, optimization

### Led architecture review session
- **Topic:** Team leadership
- **Impact:** Aligned team on database migration strategy, unblocked 3 developers
- **Tags:** leadership, architecture
```

Files are:
- **Human-readable** - Open and read them directly
- **Editable** - Make changes with any text editor
- **Version-controllable** - Commit to git for history tracking

## Dependencies

This project uses the following external libraries:

| Library | Description | Documentation |
|---------|-------------|---------------|
| [Click](https://github.com/pallets/click) | Command line interface creation toolkit | [Click Documentation](https://click.palletsprojects.com/) |
| [Questionary](https://github.com/tmbo/questionary) | Interactive command line prompts | [Questionary Documentation](https://questionary.readthedocs.io/) |
| [PyYAML](https://github.com/yaml/pyyaml) | YAML parser and emitter for Python | [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation) |
| [Rich](https://github.com/Textualize/rich) | Rich text and beautiful formatting in the terminal | [Rich Documentation](https://rich.readthedocs.io/) |

## License

MIT License - see [LICENSE](LICENSE) for details.

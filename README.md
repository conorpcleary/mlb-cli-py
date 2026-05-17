# MLB Box Score TUI

A Python-based Terminal User Interface (TUI) for Major League Baseball (MLB) scores, schedules, and standings. Built with `pytermgui` and the `MLB-StatsAPI`, featuring a modular architecture and 100% test coverage.

## Features

- **Full Season Schedule:** Navigate the entire 2026 MLB season through a dedicated calendar view or daily snapshots.
- **Dynamic Standings:** Real-time standings for all 6 MLB divisions (AL and NL), including comprehensive **Wild Card** rankings.
- **Interactive Calendar:** A multi-month calendar view for quick date selection, featuring intuitive **WASD** keyboard navigation and automatic focus management.
- **Smart Caching:** Built-in caching service to minimize API calls and ensure a responsive user experience.
- **Smooth Transitions:** Animated screen transitions for a modern, fluid feel.
- **Robust Architecture:** Surgical, class-based organization of widgets and screens for high maintainability.

## Installation

### From PyPI (Recommended)

Install the application directly using `pip`:

```bash
pip install mlb-cli-py
```

### Local Setup (Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/conorpcleary/mlb-cli-py.git
   cd mlb-cli-py
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install in editable mode:**
   ```bash
   pip install -e ".[dev]"
   ```

## Usage

After installation, run the application from anywhere in your terminal:

```bash
mlb-cli
```

## Controls

The application is designed for rapid keyboard-driven navigation.

### Global Controls

| Key | Action |
| --- | --- |
| `[` | Previous Day / Previous Calendar Page (with wrapping) |
| `]` | Next Day / Next Calendar Page (with wrapping) |
| `t` | Jump to Today's Schedule |
| `c` | Switch to Calendar View |
| `x` | Toggle Standings View |
| `ESC` | Exit the application |
| `Tab` | Cycle focus between UI components |

### Calendar Navigation

When in the Calendar view, you can use specialized keys for precise date selection:

| Key | Action |
| --- | --- |
| `W` | Move focus up one week |
| `A` | Move focus left one day |
| `S` | Move focus down one week |
| `D` | Move focus right one day |
| `Enter` | Select the focused date and view its schedule |

## Project Structure

The project follows a strict modular design optimized for distribution:

```text
mlb-cli-py/
├── pyproject.toml       # Modern build system configuration and metadata
├── app/
│   ├── mlb_cli.py       # Main application controller and TUI entry point
│   ├── models/          # Data services (API fetching, caching, date utilities)
│   ├── widgets/         # Modular TUI components (Game, Standing, Calendar widgets)
│   └── screens/         # Class-based screen definitions (Schedule, Standings, Calendar)
├── tests/               # 100% covered test suite (Unit and integration tests)
└── README.md            # You are here!
```

## Development & Testing

The project maintains a perfect **10.00/10 Pylint score** and **100% test coverage**.

### Running Tests

To run the full test suite using `pytest`:

```bash
PYTHONPATH=. pytest
```

### Linting

To verify code quality:

```bash
pylint app tests
```

## Release Workflow

This project uses an automated release pipeline to publish updates to PyPI:

1. **Version Bump:** Update the version in `pyproject.toml`.
2. **GitHub Release:** Create and publish a new Release on GitHub with a version tag (e.g., `v0.1.0`).
3. **Automated Publish:** A GitHub Action is triggered by the release, which:
   - Builds the source distribution and wheel.
   - Publishes the package to PyPI using **Trusted Publishing (OIDC)**.

## Acknowledgements

This project would not be possible without the [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI) and [PyTermGUI](https://github.com/bczsalba/pytermgui) projects.

## License

MIT License - see [LICENSE](LICENSE) for details.

# MLB Box Score TUI

A high-performance, Python-based Terminal User Interface (TUI) for Major League Baseball (MLB) scores, schedules, and standings. Built with `pytermgui` and the `MLB-StatsAPI`, featuring a modular architecture and 100% test coverage.

## Features

- **Full Season Schedule:** Navigate the entire 2026 MLB season through a dedicated calendar view or daily snapshots.
- **Dynamic Standings:** Real-time standings for all 6 MLB divisions (AL and NL), including comprehensive **Wild Card** rankings.
- **Interactive Calendar:** A multi-month calendar view for quick date selection, featuring intuitive **WASD** keyboard navigation and automatic focus management.
- **Smart Caching:** Built-in caching service to minimize API calls and ensure a responsive user experience.
- **Smooth Transitions:** Animated screen transitions for a modern, fluid feel.
- **Robust Architecture:** Surgical, class-based organization of widgets and screens for high maintainability.

## Installation

### Prerequisites

- Python 3.10+
- A terminal with support for box-drawing characters and ANSI colors.

### Setup

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

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application using the main entry point:

```bash
python3 mlb_cli.py
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

The project follows a strict modular design:

```text
mlb-cli-py/
├── mlb_cli.py           # Main application controller and state management
├── app/
│   ├── models/          # Data services (API fetching, caching, date utilities)
│   ├── widgets/         # Modular TUI components (Game, Standing, Calendar widgets)
│   └── screens/         # Class-based screen definitions (Schedule, Standings, Calendar)
├── tests/               # 100% covered test suite (Unit and integration tests)
├── requirements.txt     # Project dependencies
└── README.md            # You are here!
```

## Development & Testing

The project maintains a perfect **10.00/10 Pylint score** and **100% test coverage**.

### Running Tests

To run the full test suite using `pytest`:

```bash
pytest
```

To run tests with coverage reporting:

```bash
pytest --cov=app --cov=mlb_cli tests/
```

### Linting

To verify code quality:

```bash
pylint mlb_cli.py app tests
```

## Acknowledgements

This project would not be possible without the [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI) and [PyTermGUI](https://github.com/bczsalba/pytermgui) projects.

## License

MIT License - see [LICENSE](LICENSE) for details.

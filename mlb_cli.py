"""
Main entry point for the MLB CLI application.
This module initializes the Terminal UI and manages the primary window and global keybindings.
"""
import pytermgui as ptg
from app.models.data_service import fetch_teams
from app.screens.main_screens import (
    get_yesterday_widgets,
    get_today_widgets,
    get_standings_widgets
)
from app.widgets.animations import slide_transition


class MLBApp:
    """
    Main application class that manages the WindowManager and screen transitions.
    """

    def __init__(self):
        """Initializes the application state and UI components."""
        fetch_teams()
        self.manager = ptg.WindowManager()
        self.static_width = 80
        self.static_height = 0  # Will be set in run()
        self.main_window = None
        self.is_initialized = False
        self.active_page = None

    def set_window_data(self, widgets, title, page_name):
        """Sets content for the main window, using animation if already initialized."""
        if self.active_page == page_name:
            return

        self.active_page = page_name
        if not self.is_initialized:
            self.is_initialized = True
            self.main_window.set_widgets(widgets)
            self.main_window.set_title(title)
            self.main_window.width = self.static_width
            self.main_window.height = self.static_height
            self.main_window.styles.border = "green"
            self.main_window.styles.corner = "green"
            self.main_window.center()
            return

        slide_transition(self.main_window, self.manager, widgets, title)

    def update_to_yesterday(self, *_args, **_kwargs):
        """Transitions the main window to show yesterday's scores."""
        widgets, title = get_yesterday_widgets(
            self.update_to_today, self.update_to_standings)
        self.set_window_data(widgets, title, "yesterday")
        return True

    def update_to_today(self, *_args, **_kwargs):
        """Transitions the main window to show today's schedule."""
        widgets, title = get_today_widgets(
            self.update_to_yesterday, self.update_to_standings)
        self.set_window_data(widgets, title, "today")
        return True

    def update_to_standings(self, *_args, **_kwargs):
        """Transitions the main window to show current MLB standings."""
        widgets, title = get_standings_widgets(self.update_to_yesterday)
        self.set_window_data(widgets, title, "standings")
        return True

    def exit_app(self, *_args, **_kwargs):
        """Stops the WindowManager and exits the application."""
        self.manager.stop()
        return True

    def run(self):
        """Starts the application main loop."""
        with self.manager:
            self.static_height = min(30, self.manager.terminal.height - 2)

            self.main_window = ptg.Window(
                width=self.static_width,
                height=self.static_height,
                is_static=True,
                is_noresize=True)
            self.manager.add(self.main_window)

            # Initial content
            self.update_to_yesterday()

            # Global bindings
            self.manager.bind("[", self.update_to_yesterday)
            self.manager.bind("]", self.update_to_today)
            self.manager.bind("s", self.update_to_standings)
            self.manager.bind(ptg.keys.ESC, self.exit_app)

            self.manager.run()


def main():
    """Entry point for the application."""
    app = MLBApp()
    app.run()


if __name__ == "__main__":
    main()

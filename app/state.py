"""
Application state management for the MLB CLI application.
Handles dates, page tracking, and navigation logic.
"""
from datetime import datetime, timedelta


class ApplicationState:
    """
    Manages the persistent state of the application.
    Tracks the current date, active page, and calendar pagination.
    """

    def __init__(self):
        self.current_date = datetime.now()
        self.active_page = None
        self.calendar_page = 0
        self.determine_initial_calendar_page()

    def determine_initial_calendar_page(self):
        """Determines the calendar page based on current_date."""
        month = self.current_date.month
        if month <= 5:
            self.calendar_page = 0
        elif month <= 8:
            self.calendar_page = 1
        else:
            self.calendar_page = 2

    def increment_date(self):
        """Increments the current date, with season boundary logic."""
        if self.current_date.year < 2026:
            self.current_date = datetime(2026, 1, 1)

        if self.current_date < datetime(2026, 12, 31):
            self.current_date += timedelta(days=1)
            return True
        return False

    def decrement_date(self):
        """Decrements the current date, with season boundary logic."""
        if self.current_date.year > 2026:
            self.current_date = datetime(2026, 12, 31)

        if self.current_date > datetime(2026, 1, 1):
            self.current_date -= timedelta(days=1)
            return True
        return False

    def next_calendar_page(self):
        """Moves to the next calendar page with wrapping."""
        self.calendar_page = (self.calendar_page + 1) % 3

    def prev_calendar_page(self):
        """Moves to the previous calendar page with wrapping."""
        self.calendar_page = (self.calendar_page - 1) % 3

    def reset_to_today(self):
        """Resets current_date to the actual today."""
        self.current_date = datetime.now()

    def set_active_page(self, page_name):
        """Updates the active page name."""
        self.active_page = page_name

    @property
    def on_calendar_screen(self):
        """Returns True if currently on a calendar page."""
        return self.active_page and self.active_page.startswith("calendar")

    @property
    def on_standings_screen(self):
        """Returns True if currently on the standings page."""
        return self.active_page == "standings"

    @property
    def on_box_score_screen(self):
        """Returns True if currently on a box score page."""
        return self.active_page and self.active_page.startswith("boxscore")

"""
Main entry point for the MLB CLI application.
This module initializes the Terminal UI and manages the primary window and global keybindings.
"""
from datetime import datetime, timedelta
import pytermgui as ptg
from .models.data_service import (
    fetch_teams,
    format_date
)
from .screens import (
    ScheduleScreen,
    StandingsScreen,
    CalendarScreen,
    ErrorScreen,
    BoxScoreScreen
)
from .widgets import CalendarWidget, GameWidget, slide_transition
from .config import STATIC_WIDTH, INITIAL_HEIGHT
from .state import ApplicationState
from .exceptions import APIError
from .logger import get_logger

logger = get_logger(__name__)


class MLBApp:
    """
    TUI Manager class for the MLB CLI application.
    Handles window management, screen transitions, and global keybindings.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        """Initializes the application UI and logic state."""
        fetch_teams()
        self.manager = ptg.WindowManager()
        self.state = ApplicationState()
        self.static_width = STATIC_WIDTH
        self.static_height = 0  # Will be set in run()
        self.main_window = None
        self.is_initialized = False

    def set_window_data(self, widgets, title, page_name, on_finish=None):
        """Sets content for the main window, using animation if already initialized."""
        if self.state.active_page == page_name:
            if on_finish:
                on_finish()
            return

        # Calculate required height based on content
        max_height = self.manager.terminal.height - 2
        temp_window = ptg.Window(*widgets, width=self.static_width)
        temp_window.set_title(title)
        target_height = min(max_height, temp_window.height)

        self.state.set_active_page(page_name)
        if not self.is_initialized:
            self.is_initialized = True
            self.main_window.set_widgets(widgets)
            self.main_window.set_title(title)
            self.main_window.width = self.static_width
            self.main_window.height = target_height
            self.main_window.styles.border = "green"
            self.main_window.styles.corner = "green"
            self.main_window.center()
            if on_finish:
                on_finish()
            return

        slide_transition(
            self.main_window,
            self.manager,
            widgets,
            title,
            on_finish=on_finish,
            new_height=target_height
        )

    @staticmethod
    def handle_errors(func):
        """Decorator to handle errors during screen transitions."""
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except (APIError, Exception) as e:  # pylint: disable=broad-exception-caught
                logger.error("Error in %s: %s", func.__name__, e, exc_info=True)
                # Provide a user-friendly message for generic exceptions
                msg = str(e) if isinstance(e, APIError) else "An unexpected error occurred"
                widgets, title = ErrorScreen.get_widgets(msg)
                self.set_window_data(widgets, title, "error")
                return False
        return wrapper

    @handle_errors
    def update_to_schedule(self, *_args, **_kwargs):
        """Transitions the main window to show the schedule for current_date."""
        date_str = format_date(self.state.current_date)
        widgets, title = ScheduleScreen.get_widgets(
            date_str,
            on_game_selected=self.update_to_box_score
        )
        self.set_window_data(
            widgets,
            title,
            f"schedule:{date_str}",
            on_finish=self._focus_first_game_in_schedule
        )
        return True

    def _focus_first_game_in_schedule(self):
        """Finds and focuses the first GameWidget in the schedule."""
        for i, (selectable, _) in enumerate(self.main_window.selectables):
            if isinstance(selectable, GameWidget):
                self.main_window.select(i)
                self.manager.focused = selectable
                return True
        return False

    @handle_errors
    def update_to_box_score(self, game_id):
        """Transitions to the box score view."""
        widgets, title = BoxScoreScreen.get_widgets(game_id)
        self.set_window_data(widgets, title, f"boxscore:{game_id}")
        return True

    def handle_back(self, *_args, **_kwargs):
        """Returns from box score to schedule, or handles other back logic."""
        if self.state.on_box_score_screen:
            return self.update_to_schedule()
        return False

    def go_to_previous_day(self, *_args, **_kwargs):
        """Decrements the current date or page."""
        if self.state.on_calendar_screen:
            return self.go_to_previous_page()

        if self.state.decrement_date():
            return self.update_to_schedule()
        return True

    def go_to_next_day(self, *_args, **_kwargs):
        """Increments the current date or page."""
        if self.state.on_calendar_screen:
            return self.go_to_next_page()

        if self.state.increment_date():
            return self.update_to_schedule()
        return True

    @handle_errors
    def toggle_standings(self, *_args, **_kwargs):
        """Toggles between standings and schedule/calendar."""
        if self.state.on_standings_screen:
            return self.update_to_schedule()

        widgets, title = StandingsScreen.get_widgets()
        self.set_window_data(widgets, title, "standings")
        return True

    @handle_errors
    def update_to_calendar(self, *_args, sync_page=True, focus_target=None, **_kwargs):
        """Transitions to the calendar view."""
        if self.state.on_standings_screen:
            self.state.reset_to_today()

        if sync_page:
            # Ensure calendar_page matches current_date
            self.state.determine_initial_calendar_page()

        pages = [
            [3, 4, 5],
            [6, 7, 8],
            [9, 10]
        ]
        months = pages[self.state.calendar_page]
        widgets, title = CalendarScreen.get_widgets(
            2026,
            months,
            self.on_calendar_date_selected,
            selected_date=self.state.current_date
        )
        self.set_window_data(
            widgets,
            title,
            f"calendar:{self.state.calendar_page}",
            on_finish=lambda: self._focus_current_date_in_calendar(target=focus_target)
        )
        return True

    def _focus_current_date_in_calendar(self, target=None):
        # pylint: disable=too-many-branches
        """
        Helper to find and focus a date in the calendar view.
        If target is None, focuses current_date.
        If target is 'first', focuses first date of first month.
        If target is 'last', focuses last date of last month.
        """
        calendar_widgets = []
        for widget in self.main_window:
            if not isinstance(widget, ptg.Container):
                continue
            for sub in widget:
                if isinstance(sub, CalendarWidget):
                    calendar_widgets.append(sub)

        if not calendar_widgets:
            return False

        target_btn = None
        if target == "first":
            sub = calendar_widgets[0]
            first_day = min(sub.day_to_button.keys())
            target_btn = sub.day_to_button[first_day]
        elif target == "last":
            sub = calendar_widgets[-1]
            last_day = max(sub.day_to_button.keys())
            target_btn = sub.day_to_button[last_day]
        else:
            # Default: focus current_date
            for sub in calendar_widgets:
                if sub.month == self.state.current_date.month:
                    day = self.state.current_date.day
                    if day in sub.day_to_button:
                        target_btn = sub.day_to_button[day]
                        break

        if target_btn:
            for i, (selectable, _) in enumerate(self.main_window.selectables):
                if selectable is target_btn:
                    self.main_window.select(i)
                    self.manager.focused = target_btn
                    return True
        return False

    def on_calendar_date_selected(self, year, month, day):
        """Callback for when a date is selected in the calendar."""
        self.state.current_date = datetime(year, month, day)
        return self.update_to_schedule()

    def _navigate_calendar(self, direction):
        # pylint: disable=too-many-branches
        """
        Global WASD navigation for the calendar.
        Moves focus between buttons based on date logic.
        """
        if not self.state.on_calendar_screen:
            return False

        focused = self.manager.focused
        if focused is None:
            return False

        # Find which CalendarWidget the focused button belongs to
        target_widget = None
        for widget in self.main_window:
            if not isinstance(widget, ptg.Container):
                continue
            for sub in widget:
                if isinstance(sub, CalendarWidget) and focused in sub.button_to_day:
                    target_widget = sub
                    break
            if target_widget:
                break

        if not target_widget:
            return False

        day = target_widget.button_to_day[focused]
        current_date = datetime(target_widget.year, target_widget.month, day)

        delta = {
            "w": timedelta(days=-7),
            "a": timedelta(days=-1),
            "s": timedelta(days=7),
            "d": timedelta(days=1),
        }.get(direction)

        if not delta:
            return False

        target_date = current_date + delta

        # Look for the target date in any CalendarWidget in the main window
        for widget in self.main_window:
            if not isinstance(widget, ptg.Container):
                continue
            for sub in widget:
                if not (isinstance(sub, CalendarWidget) and
                        sub.year == target_date.year and
                        sub.month == target_date.month):
                    continue

                if target_date.day in sub.day_to_button:
                    target_btn = sub.day_to_button[target_date.day]
                    # Find and select the button index in the window
                    for i, (selectable, _) in enumerate(self.main_window.selectables):
                        if selectable is target_btn:
                            self.main_window.select(i)
                            self.manager.focused = target_btn
                            return True
        return False

    def go_to_previous_page(self, *_args, **_kwargs):
        """Moves calendar view to the previous page with wrapping."""
        self.state.prev_calendar_page()
        return self.update_to_calendar(sync_page=False, focus_target="last")

    def go_to_next_page(self, *_args, **_kwargs):
        """Moves calendar view to the next page with wrapping."""
        self.state.next_calendar_page()
        return self.update_to_calendar(sync_page=False, focus_target="first")

    def go_to_today(self, *_args, **_kwargs):
        """Resets the current date to today and updates the view."""
        self.state.reset_to_today()
        return self.update_to_schedule()

    def exit_app(self, *_args, **_kwargs):
        """Stops the WindowManager and exits the application."""
        self.manager.stop()
        return True

    def run(self):
        """Starts the application main loop."""
        with self.manager:
            self.static_height = min(INITIAL_HEIGHT, self.manager.terminal.height - 2)

            self.main_window = ptg.Window(
                width=self.static_width,
                height=self.static_height,
                is_static=True,
                is_noresize=True)
            self.manager.add(self.main_window)

            # Initial content: Calendar
            self.update_to_calendar()

            # Global bindings
            self.manager.bind("[", self.go_to_previous_day)
            self.manager.bind("]", self.go_to_next_day)
            self.manager.bind("t", self.go_to_today)
            self.manager.bind("c", self.update_to_calendar)
            self.manager.bind("x", self.toggle_standings)
            self.manager.bind("q", self.handle_back)
            self.manager.bind(ptg.keys.ESC, self.exit_app)

            # WASD for Calendar Navigation
            self.manager.bind("w", lambda *_: self._navigate_calendar("w"))
            self.manager.bind("a", lambda *_: self._navigate_calendar("a"))
            self.manager.bind("s", lambda *_: self._navigate_calendar("s"))
            self.manager.bind("d", lambda *_: self._navigate_calendar("d"))

            self.manager.run()


def main():
    """Entry point for the application."""
    app = MLBApp()
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()

"""
Unit tests for the main mlb_cli application.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytermgui as ptg
from mlb_cli import MLBApp, main
from app.widgets import CalendarWidget

class TestMLBApp(unittest.TestCase):
    """Test cases for the MLBApp class."""
    # pylint: disable=too-many-public-methods,protected-access

    def setUp(self):
        """Initialize MLBApp with mocked WindowManager."""
        with patch('mlb_cli.fetch_teams'), \
             patch('mlb_cli.ptg.WindowManager') as mock_manager:
            self.app = MLBApp()
            self.app.manager = mock_manager.return_value
            self.app.main_window = MagicMock(spec=ptg.Window)
            self.app.main_window.__iter__.return_value = iter([])

    def test_init(self):
        """Test MLBApp initialization."""
        self.assertEqual(self.app.static_width, 80)
        self.assertFalse(self.app.is_initialized)
        self.assertIsNone(self.app.active_page)

    def test_set_window_data_initial(self):
        """Test initial call to set_window_data."""
        widgets = [ptg.Label("test")]
        self.app.set_window_data(widgets, "Title", "page1")

        self.assertTrue(self.app.is_initialized)
        self.assertEqual(self.app.active_page, "page1")
        self.app.main_window.set_widgets.assert_called_with(widgets)
        self.app.main_window.set_title.assert_called_with("Title")

    def test_set_window_data_same_page(self):
        """Test set_window_data with the same page name does nothing."""
        self.app.active_page = "page1"
        self.app.main_window.set_widgets.reset_mock()
        self.app.set_window_data([], "Title", "page1")
        self.app.main_window.set_widgets.assert_not_called()

    def test_go_to_previous_day_limits(self):
        """Test season boundaries for previous day."""
        # Test upper limit (should snap to 2026/12/30)
        self.app.current_date = datetime(2027, 1, 1)
        with patch.object(self.app, 'update_to_schedule'):
            self.app.go_to_previous_day()
            self.assertEqual(self.app.current_date, datetime(2026, 12, 30))

        # Test lower limit (should not decrement)
        self.app.current_date = datetime(2026, 1, 1)
        self.assertTrue(self.app.go_to_previous_day())
        self.assertEqual(self.app.current_date, datetime(2026, 1, 1))

    def test_go_to_next_day_limits(self):
        """Test season boundaries for next day."""
        # Test lower limit (should snap to 2026/01/02)
        self.app.current_date = datetime(2025, 1, 1)
        with patch.object(self.app, 'update_to_schedule'):
            self.app.go_to_next_day()
            self.assertEqual(self.app.current_date, datetime(2026, 1, 2))

        # Test upper limit (should not increment)
        self.app.current_date = datetime(2026, 12, 31)
        self.assertTrue(self.app.go_to_next_day())
        self.assertEqual(self.app.current_date, datetime(2026, 12, 31))

    def test_focus_current_date_in_calendar(self):
        """Test _focus_current_date_in_calendar with various widget structures."""
        # Miss: empty window
        self.app.main_window.__iter__.return_value = iter([])
        self.assertFalse(self.app._focus_current_date_in_calendar())

        # Miss: not a container
        self.app.main_window.__iter__.return_value = iter([ptg.Label("test")])
        self.assertFalse(self.app._focus_current_date_in_calendar())

        # Hit: deep structure
        mock_btn = MagicMock(spec=ptg.Button)
        mock_cal = MagicMock(spec=CalendarWidget)
        mock_cal.month = self.app.current_date.month
        mock_cal.day_to_button = {self.app.current_date.day: mock_btn}

        mock_container = MagicMock(spec=ptg.Container)
        mock_container.__iter__.return_value = iter([mock_cal])

        self.app.main_window.__iter__.return_value = iter([mock_container])
        self.app.main_window.selectables = [(mock_btn, 0)]

        self.assertTrue(self.app._focus_current_date_in_calendar())
        self.app.main_window.select.assert_called_with(0)
        self.assertEqual(self.app.manager.focused, mock_btn)

    @patch('mlb_cli.slide_transition')
    def test_set_window_data_transition(self, mock_transition):
        """Test set_window_data triggers slide_transition for subsequent calls."""
        self.app.is_initialized = True
        self.app.active_page = "page1"
        widgets = [ptg.Label("test")]

        self.app.set_window_data(widgets, "New Title", "page2")

        self.assertEqual(self.app.active_page, "page2")
        mock_transition.assert_called_once()

    def test_determine_initial_calendar_page(self):
        """Test initial calendar page based on month."""
        # Page 0 (<= May)
        self.app.current_date = datetime(2026, 3, 15)
        self.app._determine_initial_calendar_page()
        self.assertEqual(self.app.calendar_page, 0)

        # Page 1 (<= Aug)
        self.app.current_date = datetime(2026, 7, 15)
        self.app._determine_initial_calendar_page()
        self.assertEqual(self.app.calendar_page, 1)

        # Page 2 (> Aug)
        self.app.current_date = datetime(2026, 10, 15)
        self.app._determine_initial_calendar_page()
        self.assertEqual(self.app.calendar_page, 2)

    def test_go_to_previous_day_calendar(self):
        """Test go_to_previous_day while on calendar redirects to page."""
        self.app.active_page = "calendar:0"
        with patch.object(self.app, 'go_to_previous_page') as mock_go:
            self.app.go_to_previous_day()
            mock_go.assert_called_once()

    def test_go_to_next_day_calendar(self):
        """Test go_to_next_day while on calendar redirects to page."""
        self.app.active_page = "calendar:0"
        with patch.object(self.app, 'go_to_next_page') as mock_go:
            self.app.go_to_next_day()
            mock_go.assert_called_once()

    def test_go_to_previous_page_boundary(self):
        """Test boundary for go_to_previous_page (wraps)."""
        self.app.calendar_page = 0
        self.assertTrue(self.app.go_to_previous_page())
        self.assertEqual(self.app.calendar_page, 2)

    def test_go_to_next_page_boundary(self):
        """Test boundary for go_to_next_page (wraps)."""
        self.app.calendar_page = 2
        self.assertTrue(self.app.go_to_next_page())
        self.assertEqual(self.app.calendar_page, 0)

    def test_focus_current_date_in_calendar_day_missing(self):
        """Test _focus_current_date_in_calendar when day is missing from button map."""
        mock_cal = MagicMock(spec=CalendarWidget)
        mock_cal.month = self.app.current_date.month
        mock_cal.day_to_button = {} # Day missing

        mock_container = MagicMock(spec=ptg.Container)
        mock_container.__iter__.return_value = iter([mock_cal])

        self.app.main_window.__iter__.return_value = iter([mock_container])
        self.assertFalse(self.app._focus_current_date_in_calendar())

    def test_focus_current_date_in_calendar_month_mismatch(self):
        """Test _focus_current_date_in_calendar when month doesn't match."""
        mock_cal = MagicMock(spec=CalendarWidget)
        mock_cal.month = self.app.current_date.month + 1 # Mismatch

        mock_container = MagicMock(spec=ptg.Container)
        mock_container.__iter__.return_value = iter([mock_cal])

        self.app.main_window.__iter__.return_value = iter([mock_container])
        self.assertFalse(self.app._focus_current_date_in_calendar())

    @patch('mlb_cli.ScheduleScreen.get_widgets')
    def test_update_to_schedule(self, mock_get):
        """Test transition to schedule."""
        mock_get.return_value = ([], "Schedule")
        self.app.update_to_schedule()
        self.assertTrue(self.app.active_page.startswith("schedule:"))

    def test_go_to_previous_day(self):
        """Test decrementing current date."""
        initial_date = self.app.current_date
        with patch.object(self.app, 'update_to_schedule'):
            self.app.go_to_previous_day()
            self.assertEqual(self.app.current_date, initial_date - timedelta(days=1))

    def test_go_to_next_day(self):
        """Test incrementing current date."""
        initial_date = self.app.current_date
        with patch.object(self.app, 'update_to_schedule'):
            self.app.go_to_next_day()
            self.assertEqual(self.app.current_date, initial_date + timedelta(days=1))

    def test_go_to_today(self):
        """Test resetting current date to today."""
        self.app.current_date = datetime(2026, 10, 1)
        with patch.object(self.app, 'update_to_schedule'):
            self.app.go_to_today()
            # It should be today now
            self.assertEqual(
                self.app.current_date.strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            )

    @patch('mlb_cli.CalendarScreen.get_widgets')
    def test_update_to_calendar(self, mock_get):
        """Test transition to calendar."""
        mock_get.return_value = ([], "Calendar")
        self.app.update_to_calendar()
        self.assertEqual(self.app.active_page, f"calendar:{self.app.calendar_page}")

    @patch('mlb_cli.CalendarScreen.get_widgets')
    def test_update_to_calendar_from_standings(self, mock_get):
        """Test that date is reset when returning from standings."""
        mock_get.return_value = ([], "Calendar")
        self.app.active_page = "standings"
        self.app.current_date = datetime(2026, 1, 1)

        self.app.update_to_calendar()

        # Should be today
        self.assertEqual(
            self.app.current_date.strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d')
        )

    def test_go_to_previous_page(self):
        """Test decrementing calendar page with wrapping."""
        self.app.calendar_page = 0
        with patch.object(self.app, 'update_to_calendar'):
            self.app.go_to_previous_page()
            self.assertEqual(self.app.calendar_page, 2)

    def test_go_to_next_page(self):
        """Test incrementing calendar page with wrapping."""
        self.app.calendar_page = 2
        with patch.object(self.app, 'update_to_calendar'):
            self.app.go_to_next_page()
            self.assertEqual(self.app.calendar_page, 0)

    def test_pagination_no_mock(self):
        """Test that pagination actually works without mocking update_to_calendar."""
        # Set date to May (should be page 0)
        self.app.current_date = datetime(2026, 5, 15)
        self.app.calendar_page = 0

        # We need to mock CalendarScreen.get_widgets to avoid real UI creation issues in test
        with patch('app.screens.CalendarScreen.get_widgets') as mock_get:
            mock_get.return_value = ([], "Title")

            # Go to next page
            self.app.go_to_next_page()

            self.assertEqual(self.app.calendar_page, 1)

    def test_on_calendar_date_selected(self):
        """Test selecting a date from calendar."""
        with patch.object(self.app, 'update_to_schedule'):
            self.app.on_calendar_date_selected(2026, 5, 20)
            self.assertEqual(self.app.current_date.year, 2026)
            self.assertEqual(self.app.current_date.month, 5)
            self.assertEqual(self.app.current_date.day, 20)

    def test_navigate_calendar_state_checks(self):
        """Test _navigate_calendar basic state checks."""
        # 1. Not on calendar page
        self.app.active_page = "schedule"
        self.assertFalse(self.app._navigate_calendar("w"))

        # 2. On calendar page, but nothing focused
        self.app.active_page = "calendar:0"
        self.app.manager.focused = None
        self.assertFalse(self.app._navigate_calendar("w"))

    def test_navigate_calendar_success(self):
        """Test successful WASD navigation in calendar."""
        self.app.active_page = "calendar:0"

        # Create CalendarWidget with day 1 and day 2
        mock_on_selected = MagicMock()
        cal = CalendarWidget(2026, 5, mock_on_selected)
        btn1 = cal.day_to_button[1]
        btn2 = cal.day_to_button[2]

        # Put button 1 in focus
        self.app.manager.focused = btn1

        # Real Container with CalendarWidget
        real_container = ptg.Container(cal)

        self.app.main_window.__iter__.side_effect = lambda: iter([real_container])
        # selectables: (button, index)
        self.app.main_window.selectables = [(btn1, 0), (btn2, 1)]

        # Move right ('d') from day 1 to day 2
        self.assertTrue(self.app._navigate_calendar("d"))
        self.app.main_window.select.assert_called_with(1)
        self.assertEqual(self.app.manager.focused, btn2)

    def test_navigate_calendar_invalid_direction(self):
        """Test _navigate_calendar with invalid direction."""
        self.app.active_page = "calendar:0"
        cal = CalendarWidget(2026, 5, MagicMock())
        btn1 = cal.day_to_button[1]
        self.app.manager.focused = btn1

        real_container = ptg.Container(cal)
        self.app.main_window.__iter__.side_effect = lambda: iter([real_container])

        self.assertFalse(self.app._navigate_calendar("z"))

    def test_navigate_calendar_target_not_found(self):
        """Test _navigate_calendar when target button is not in view."""
        self.app.active_page = "calendar:0"
        cal = CalendarWidget(2026, 5, MagicMock())
        btn31 = cal.day_to_button[31] # Last day of May
        self.app.manager.focused = btn31

        real_container = ptg.Container(cal)
        self.app.main_window.__iter__.side_effect = lambda: iter([real_container])

        # Move right ('d') from May 31 should look for June 1, which isn't in May 2026 widget
        self.assertFalse(self.app._navigate_calendar("d"))

    def test_navigate_calendar_not_a_container(self):
        """Test _navigate_calendar skips non-container widgets in both loops."""
        self.app.active_page = "calendar:0"

        cal = CalendarWidget(2026, 5, MagicMock())
        btn1 = cal.day_to_button[1]
        self.app.manager.focused = btn1

        real_container = ptg.Container(cal)
        # Yield a Label THEN a Container to hit first loop's continue
        # Then yield a Label THEN a Container to hit second loop's continue
        self.app.main_window.__iter__.side_effect = [
            iter([ptg.Label("test"), real_container]), # First loop
            iter([ptg.Label("test"), real_container])  # Second loop
        ]

        btn2 = cal.day_to_button[2]
        self.app.main_window.selectables = [(btn1, 0), (btn2, 1)]

        self.assertTrue(self.app._navigate_calendar("d"))

    def test_navigate_calendar_focused_not_in_calendar(self):
        """Test _navigate_calendar when focused widget is not in a CalendarWidget."""
        self.app.active_page = "calendar:0"
        mock_btn = MagicMock(spec=ptg.Button)
        self.app.manager.focused = mock_btn

        # Container with a non-calendar widget
        real_container = ptg.Container(ptg.Label("test"))

        self.app.main_window.__iter__.side_effect = lambda: iter([real_container])
        self.assertFalse(self.app._navigate_calendar("d"))

    def test_navigate_calendar_target_not_calendar_widget(self):
        """Test _navigate_calendar skips non-calendar sub-widgets when looking for target."""
        self.app.active_page = "calendar:0"

        cal = CalendarWidget(2026, 5, MagicMock())
        btn1 = cal.day_to_button[1]
        self.app.manager.focused = btn1

        # Container with the current calendar and a non-calendar widget
        real_container = ptg.Container(cal, ptg.Label("test"))

        self.app.main_window.__iter__.side_effect = lambda: iter([real_container])

        # Move to a date that won't be found (to trigger the full loop)
        self.assertFalse(self.app._navigate_calendar("w")) # May 1 -> April 24 (not in May cal)

    def test_navigate_calendar_cross_widget(self):
        """Test navigation between two different CalendarWidgets."""
        self.app.active_page = "calendar:0"

        cal1 = CalendarWidget(2026, 5, MagicMock()) # May
        cal2 = CalendarWidget(2026, 6, MagicMock()) # June

        btn_may31 = cal1.day_to_button[31]
        btn_june1 = cal2.day_to_button[1]

        self.app.manager.focused = btn_may31

        real_container1 = ptg.Container(cal1)
        real_container2 = ptg.Container(cal2)

        self.app.main_window.__iter__.side_effect = lambda: iter([real_container1, real_container2])
        self.app.main_window.selectables = [(btn_may31, 0), (btn_june1, 1)]

        # Move right ('d') from May 31 to June 1
        self.assertTrue(self.app._navigate_calendar("d"))
        self.app.main_window.select.assert_called_with(1)
        self.assertEqual(self.app.manager.focused, btn_june1)

    @patch('mlb_cli.StandingsScreen.get_widgets')
    def test_toggle_standings(self, mock_get):
        """Test transition to standings and back."""
        mock_get.return_value = ([], "Standings")

        # Go to standings
        self.app.toggle_standings()
        self.assertEqual(self.app.active_page, "standings")

        # Go back to schedule
        with patch.object(self.app, 'update_to_schedule') as mock_update:
            self.app.toggle_standings()
            mock_update.assert_called_once()

    def test_exit_app(self):
        """Test application exit."""
        self.app.exit_app()
        self.app.manager.stop.assert_called_once()

    @patch('mlb_cli.ptg.Window')
    def test_run(self, _mock_window):
        """Test main run loop setup."""
        # Mock terminal height
        self.app.manager.terminal.height = 40

        # Mock run to exit immediately
        self.app.manager.run.side_effect = None

        with patch.object(self.app, 'update_to_calendar') as mock_update:
            self.app.run()

            self.app.manager.add.assert_called_once()
            mock_update.assert_called_once()
            self.app.manager.run.assert_called_once()

    @patch('mlb_cli.MLBApp')
    def test_main(self, mock_app_class):
        """Test the main() entry point."""
        mock_app_instance = mock_app_class.return_value
        main()
        mock_app_class.assert_called_once()
        mock_app_instance.run.assert_called_once()

if __name__ == '__main__':  # pragma: no cover
    unittest.main()

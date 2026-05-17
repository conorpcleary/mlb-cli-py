"""
Unit tests for calendar-specific interactions in MLBApp.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytermgui as ptg
from mlb_cli import MLBApp
from app.widgets import CalendarWidget


class TestCalendarInteraction(unittest.TestCase):
    """Test cases for WASD navigation and date selection in the calendar."""
    # pylint: disable=protected-access,duplicate-code

    def setUp(self):
        """Initialize MLBApp with mocked WindowManager."""
        with patch('mlb_cli.fetch_teams'), \
             patch('mlb_cli.ptg.WindowManager') as mock_manager:
            self.app = MLBApp()
            self.app.manager = mock_manager.return_value
            self.app.manager.terminal.width = 100
            self.app.manager.terminal.height = 40
            self.app.main_window = MagicMock(spec=ptg.Window)
            self.app.main_window.__iter__.return_value = iter([])

    def test_focus_current_date_in_calendar(self):
        """Test _focus_current_date_in_calendar with various widget structures."""
        # Hit: deep structure
        mock_btn = MagicMock(spec=ptg.Button)
        mock_cal = MagicMock(spec=CalendarWidget)
        mock_cal.month = self.app.state.current_date.month
        mock_cal.day_to_button = {self.app.state.current_date.day: mock_btn}

        mock_container = MagicMock(spec=ptg.Container)
        mock_container.__iter__.return_value = iter([mock_cal])

        self.app.main_window.__iter__.return_value = iter([mock_container])
        self.app.main_window.selectables = [(mock_btn, 0)]

        self.assertTrue(self.app._focus_current_date_in_calendar())
        self.app.main_window.select.assert_called_with(0)
        self.assertEqual(self.app.manager.focused, mock_btn)

    def test_focus_current_date_in_calendar_not_a_container(self):
        """Test _focus_current_date_in_calendar skips non-container widgets."""
        self.app.main_window.__iter__.return_value = iter([ptg.Label("test")])
        self.assertFalse(self.app._focus_current_date_in_calendar())

    def test_focus_current_date_in_calendar_day_missing(self):
        """Test _focus_current_date_in_calendar when day is missing from button map."""
        mock_cal = MagicMock(spec=CalendarWidget)
        mock_cal.month = self.app.state.current_date.month
        mock_cal.day_to_button = {} # Day missing

        mock_container = MagicMock(spec=ptg.Container)
        mock_container.__iter__.return_value = iter([mock_cal])

        self.app.main_window.__iter__.return_value = iter([mock_container])
        self.assertFalse(self.app._focus_current_date_in_calendar())

    def test_focus_current_date_in_calendar_month_mismatch(self):
        """Test _focus_current_date_in_calendar when month doesn't match."""
        mock_cal = MagicMock(spec=CalendarWidget)
        mock_cal.month = self.app.state.current_date.month + 1 # Mismatch

        mock_container = MagicMock(spec=ptg.Container)
        mock_container.__iter__.return_value = iter([mock_cal])

        self.app.main_window.__iter__.return_value = iter([mock_container])
        self.assertFalse(self.app._focus_current_date_in_calendar())

    def test_focus_current_date_in_calendar_targets(self):
        """Test _focus_current_date_in_calendar with first/last targets."""
        mock_on_selected = MagicMock()
        cal1 = CalendarWidget(2026, 5, mock_on_selected) # May
        cal2 = CalendarWidget(2026, 6, mock_on_selected) # June

        btn_may1 = cal1.day_to_button[1]
        btn_june30 = cal2.day_to_button[30]

        real_container1 = ptg.Container(cal1)
        real_container2 = ptg.Container(cal2)
        self.app.main_window.__iter__.side_effect = lambda: iter([real_container1, real_container2])
        self.app.main_window.selectables = [(btn_may1, 0), (btn_june30, 1)]

        # 1. Test 'first'
        self.assertTrue(self.app._focus_current_date_in_calendar(target="first"))
        self.assertEqual(self.app.manager.focused, btn_may1)

        # 2. Test 'last'
        self.assertTrue(self.app._focus_current_date_in_calendar(target="last"))
        self.assertEqual(self.app.manager.focused, btn_june30)

    @patch('mlb_cli.CalendarScreen.get_widgets')
    def test_update_to_calendar(self, mock_get):
        """Test transition to calendar."""
        mock_get.return_value = ([], "Calendar")
        with patch.object(self.app, 'set_window_data', wraps=self.app.set_window_data) as mock_set:
            self.app.update_to_calendar()
            self.assertEqual(self.app.state.active_page, f"calendar:{self.app.state.calendar_page}")
            mock_set.assert_called_once()
            _, kwargs = mock_set.call_args
            self.assertTrue(callable(kwargs['on_finish']))

    @patch('mlb_cli.CalendarScreen.get_widgets')
    def test_update_to_calendar_from_standings(self, mock_get):
        """Test that date is reset when returning from standings."""
        mock_get.return_value = ([], "Calendar")
        self.app.state.active_page = "standings"
        self.app.state.current_date = datetime(2026, 1, 1)

        self.app.update_to_calendar()

        # Should be today
        self.assertEqual(
            self.app.state.current_date.strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d')
        )

    def test_go_to_previous_page(self):
        """Test decrementing calendar page with wrapping."""
        self.app.state.calendar_page = 0
        with patch.object(self.app, 'update_to_calendar'):
            self.app.go_to_previous_page()
            self.assertEqual(self.app.state.calendar_page, 2)

    def test_go_to_next_page(self):
        """Test incrementing calendar page with wrapping."""
        self.app.state.calendar_page = 2
        with patch.object(self.app, 'update_to_calendar'):
            self.app.go_to_next_page()
            self.assertEqual(self.app.state.calendar_page, 0)

    def test_pagination_no_mock(self):
        """Test that pagination actually works without mocking update_to_calendar."""
        # Set date to May (should be page 0)
        self.app.state.current_date = datetime(2026, 5, 15)
        self.app.state.calendar_page = 0

        # We need to mock CalendarScreen.get_widgets to avoid real UI creation issues in test
        with patch('app.screens.CalendarScreen.get_widgets') as mock_get:
            mock_get.return_value = ([], "Title")

            # Go to next page
            self.app.go_to_next_page()

            self.assertEqual(self.app.state.calendar_page, 1)

    def test_on_calendar_date_selected(self):
        """Test selecting a date from calendar."""
        with patch.object(self.app, 'update_to_schedule'):
            self.app.on_calendar_date_selected(2026, 5, 20)
            self.assertEqual(self.app.state.current_date.year, 2026)
            self.assertEqual(self.app.state.current_date.month, 5)
            self.assertEqual(self.app.state.current_date.day, 20)

    def test_navigate_calendar_state_checks(self):
        """Test _navigate_calendar basic state checks."""
        # 1. Not on calendar page
        self.app.state.active_page = "schedule"
        self.assertFalse(self.app._navigate_calendar("w"))

        # 2. On calendar page, but nothing focused
        self.app.state.active_page = "calendar:0"
        self.app.manager.focused = None
        self.assertFalse(self.app._navigate_calendar("w"))

    def test_navigate_calendar_success(self):
        """Test successful WASD navigation in calendar."""
        self.app.state.active_page = "calendar:0"

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
        self.app.state.active_page = "calendar:0"
        cal = CalendarWidget(2026, 5, MagicMock())
        btn1 = cal.day_to_button[1]
        self.app.manager.focused = btn1

        real_container = ptg.Container(cal)
        self.app.main_window.__iter__.side_effect = lambda: iter([real_container])

        self.assertFalse(self.app._navigate_calendar("z"))

    def test_navigate_calendar_target_not_found(self):
        """Test _navigate_calendar when target button is not in view."""
        self.app.state.active_page = "calendar:0"
        cal = CalendarWidget(2026, 5, MagicMock())
        btn31 = cal.day_to_button[31] # Last day of May
        self.app.manager.focused = btn31

        real_container = ptg.Container(cal)
        self.app.main_window.__iter__.side_effect = lambda: iter([real_container])

        # Move right ('d') from May 31 should look for June 1, which isn't in May 2026 widget
        self.assertFalse(self.app._navigate_calendar("d"))

    def test_navigate_calendar_not_a_container(self):
        """Test _navigate_calendar skips non-container widgets in both loops."""
        self.app.state.active_page = "calendar:0"

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
        self.app.state.active_page = "calendar:0"
        mock_btn = MagicMock(spec=ptg.Button)
        self.app.manager.focused = mock_btn

        # Container with a non-calendar widget
        real_container = ptg.Container(ptg.Label("test"))

        self.app.main_window.__iter__.side_effect = lambda: iter([real_container])
        self.assertFalse(self.app._navigate_calendar("d"))

    def test_navigate_calendar_target_not_calendar_widget(self):
        """Test _navigate_calendar skips non-calendar sub-widgets when looking for target."""
        self.app.state.active_page = "calendar:0"

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
        self.app.state.active_page = "calendar:0"

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


if __name__ == '__main__':
    unittest.main()

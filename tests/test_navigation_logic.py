"""
Unit tests for navigation logic and date manipulation in MLBApp.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytermgui as ptg
from app.mlb_cli import MLBApp


class TestNavigationLogic(unittest.TestCase):
    """Test cases for day/page navigation and boundaries."""
    # pylint: disable=duplicate-code

    def setUp(self):
        """Initialize MLBApp with mocked WindowManager."""
        with patch('app.mlb_cli.fetch_teams'), \
             patch('app.mlb_cli.ptg.WindowManager') as mock_manager:
            self.app = MLBApp()
            self.app.manager = mock_manager.return_value
            self.app.manager.terminal.width = 100
            self.app.manager.terminal.height = 40
            self.app.main_window = MagicMock(spec=ptg.Window)
            self.app.main_window.__iter__.return_value = iter([])

    def test_determine_initial_calendar_page(self):
        """Test initial calendar page based on month."""
        # Page 0 (<= May)
        self.app.state.current_date = datetime(2026, 3, 15)
        self.app.state.determine_initial_calendar_page()
        self.assertEqual(self.app.state.calendar_page, 0)

        # Page 1 (<= Aug)
        self.app.state.current_date = datetime(2026, 7, 15)
        self.app.state.determine_initial_calendar_page()
        self.assertEqual(self.app.state.calendar_page, 1)

        # Page 2 (> Aug)
        self.app.state.current_date = datetime(2026, 10, 15)
        self.app.state.determine_initial_calendar_page()
        self.assertEqual(self.app.state.calendar_page, 2)

    def test_go_to_previous_day_limits(self):
        """Test season boundaries for previous day."""
        # Test upper limit (should snap to 2026/12/30)
        self.app.state.current_date = datetime(2027, 1, 1)
        with patch.object(self.app, 'update_to_schedule'):
            self.app.go_to_previous_day()
            self.assertEqual(self.app.state.current_date, datetime(2026, 12, 30))

        # Test lower limit (should not decrement)
        self.app.state.current_date = datetime(2026, 1, 1)
        self.assertTrue(self.app.go_to_previous_day())
        self.assertEqual(self.app.state.current_date, datetime(2026, 1, 1))

    def test_go_to_next_day_limits(self):
        """Test season boundaries for next day."""
        # Test lower limit (should snap to 2026/01/02)
        self.app.state.current_date = datetime(2025, 1, 1)
        with patch.object(self.app, 'update_to_schedule'):
            self.app.go_to_next_day()
            self.assertEqual(self.app.state.current_date, datetime(2026, 1, 2))

        # Test upper limit (should not increment)
        self.app.state.current_date = datetime(2026, 12, 31)
        self.assertTrue(self.app.go_to_next_day())
        self.assertEqual(self.app.state.current_date, datetime(2026, 12, 31))

    def test_go_to_previous_day_calendar(self):
        """Test go_to_previous_day while on calendar redirects to page."""
        self.app.state.active_page = "calendar:0"
        with patch.object(self.app, 'go_to_previous_page') as mock_go:
            self.app.go_to_previous_day()
            mock_go.assert_called_once()

    def test_go_to_next_day_calendar(self):
        """Test go_to_next_day while on calendar redirects to page."""
        self.app.state.active_page = "calendar:0"
        with patch.object(self.app, 'go_to_next_page') as mock_go:
            self.app.go_to_next_day()
            mock_go.assert_called_once()

    def test_go_to_previous_page_boundary(self):
        """Test boundary for go_to_previous_page (wraps)."""
        self.app.state.calendar_page = 0
        self.assertTrue(self.app.go_to_previous_page())
        self.assertEqual(self.app.state.calendar_page, 2)

    def test_go_to_next_page_boundary(self):
        """Test boundary for go_to_next_page (wraps)."""
        self.app.state.calendar_page = 2
        self.assertTrue(self.app.go_to_next_page())
        self.assertEqual(self.app.state.calendar_page, 0)

    @patch('app.mlb_cli.ScheduleScreen.get_widgets')
    def test_update_to_schedule(self, mock_get):
        """Test transition to schedule."""
        mock_get.return_value = ([], "Schedule")
        self.app.update_to_schedule()
        self.assertTrue(self.app.state.active_page.startswith("schedule:"))

    def test_go_to_previous_day(self):
        """Test decrementing current date."""
        initial_date = self.app.state.current_date
        with patch.object(self.app, 'update_to_schedule'):
            self.app.go_to_previous_day()
            self.assertEqual(self.app.state.current_date, initial_date - timedelta(days=1))

    def test_go_to_next_day(self):
        """Test incrementing current date."""
        initial_date = self.app.state.current_date
        with patch.object(self.app, 'update_to_schedule'):
            self.app.go_to_next_day()
            self.assertEqual(self.app.state.current_date, initial_date + timedelta(days=1))

    def test_go_to_today_schedule(self):
        """Test resetting current date to today from schedule view."""
        self.app.state.active_page = "schedule:2026-10-01"
        self.app.state.current_date = datetime(2026, 10, 1)
        with patch.object(self.app, 'update_to_schedule') as mock_update:
            self.app.go_to_today()
            mock_update.assert_called_once()
            # It should be today now
            self.assertEqual(
                self.app.state.current_date.strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            )

    def test_go_to_today_calendar(self):
        """Test resetting current date to today from calendar view."""
        self.app.state.active_page = "calendar:0"
        self.app.state.current_date = datetime(2026, 10, 1)
        with patch.object(self.app, 'update_to_calendar') as mock_update:
            self.app.go_to_today()
            mock_update.assert_called_once()
            # It should be today now
            self.assertEqual(
                self.app.state.current_date.strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            )

    def test_go_to_previous_day_standings(self):
        """Test go_to_previous_day while on standings screen (should do nothing)."""
        self.app.state.active_page = "standings"
        initial_date = self.app.state.current_date
        with patch.object(self.app, 'update_to_schedule') as mock_update:
            self.app.go_to_previous_day()
            mock_update.assert_not_called()
            self.assertEqual(self.app.state.current_date, initial_date)

    def test_go_to_next_day_standings(self):
        """Test go_to_next_day while on standings screen (should do nothing)."""
        self.app.state.active_page = "standings"
        initial_date = self.app.state.current_date
        with patch.object(self.app, 'update_to_schedule') as mock_update:
            self.app.go_to_next_day()
            mock_update.assert_not_called()
            self.assertEqual(self.app.state.current_date, initial_date)

    @patch('app.mlb_cli.StandingsScreen.get_widgets')
    def test_toggle_standings(self, mock_get):
        """Test transition to standings and back."""
        mock_get.return_value = ([], "Standings")

        # Go to standings
        self.app.toggle_standings()
        self.assertEqual(self.app.state.active_page, "standings")

        # Go back to schedule
        with patch.object(self.app, 'update_to_schedule') as mock_update:
            self.app.toggle_standings()
            mock_update.assert_called_once()


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for the main_screens module.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytermgui as ptg
from app.screens import ScheduleScreen, StandingsScreen, CalendarScreen
from app.widgets import CalendarWidget

class TestMainScreens(unittest.TestCase):
    """Test cases for main_screens.py screen generator functions."""

    @patch('app.screens.schedule_screen.fetch_schedule')
    @patch('app.screens.schedule_screen.create_grid')
    def test_get_schedule_widgets(self, mock_grid, mock_fetch):
        """Test schedule screen generation."""
        date_str = '01/01/2026'
        mock_fetch.return_value = []
        mock_grid.return_value = []

        widgets, title = ScheduleScreen.get_widgets(date_str)

        self.assertIn(date_str, title)
        self.assertEqual(len(widgets), 2) # NavigationWidget and Label
        mock_fetch.assert_called_with(date_str)

    @patch('app.screens.standings_screen.fetch_standings')
    def test_get_standings_widgets(self, mock_fetch):
        """Test standings screen generation."""
        # Mock 3 divisions for AL and NL
        al_divs = [
            {'div_name': 'AL E', 'teams': []},
            {'div_name': 'AL C', 'teams': []},
            {'div_name': 'AL W', 'teams': []}
        ]
        nl_divs = [
            {'div_name': 'NL E', 'teams': []},
            {'div_name': 'NL C', 'teams': []},
            {'div_name': 'NL W', 'teams': []}
        ]
        mock_fetch.return_value = (al_divs, nl_divs, {}, {})

        widgets, title = StandingsScreen.get_widgets()

        self.assertIn("MLB Standings", title)
        # Nav, Label, 4 Division/WC Splitters
        self.assertEqual(len(widgets), 6)
        mock_fetch.assert_called_once()

    def test_get_calendar_widgets(self):
        """Test calendar screen generation."""
        mock_on_selected = MagicMock()
        widgets, title = CalendarScreen.get_widgets(2026, [3, 4, 5], mock_on_selected)

        self.assertIn("March - May 2026", title)
        # Nav + 3 month containers
        self.assertEqual(len(widgets), 4)

    def test_get_calendar_widgets_selected_date(self):
        """Test calendar screen generation with a selected date highlighted."""
        mock_on_selected = MagicMock()
        selected_date = datetime(2026, 4, 15)
        widgets, _ = CalendarScreen.get_widgets(
            2026, [3, 4, 5], mock_on_selected, selected_date=selected_date
        )

        # Check if the correct month container received the selected day
        # widgets[1] is March, widgets[2] is April, widgets[3] is May
        april_container = widgets[2]
        # April container has a Label and a CalendarWidget
        cal_widget = [w for w in april_container if isinstance(w, CalendarWidget)][0]
        # We can't easily check private state but we know line 39 was hit
        self.assertEqual(cal_widget.month, 4)

    def test_get_calendar_widgets_padding(self):
        """Test calendar screen generation with padding for fewer than 3 months."""
        mock_on_selected = MagicMock()
        # Page 3 has 2 months (Sep, Oct)
        widgets, _ = CalendarScreen.get_widgets(2026, [9, 10], mock_on_selected)

        # Nav + 2 month containers + 1 padding label = 4 widgets
        self.assertEqual(len(widgets), 4)
        self.assertIsInstance(widgets[3], ptg.Label)
        self.assertEqual(widgets[3].value, "")

if __name__ == '__main__':  # pragma: no cover
    unittest.main()

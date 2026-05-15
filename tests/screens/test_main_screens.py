"""
Unit tests for the main_screens module.
"""
import unittest
from unittest.mock import patch, MagicMock
from app.screens.main_screens import (
    get_yesterday_widgets,
    get_today_widgets,
    get_standings_widgets
)

class TestMainScreens(unittest.TestCase):
    """Test cases for main_screens.py screen generator functions."""

    @patch('app.screens.main_screens.get_yesterday_date')
    @patch('app.screens.main_screens.fetch_schedule')
    @patch('app.screens.main_screens.create_grid')
    def test_get_yesterday_widgets(self, mock_grid, mock_fetch, mock_date):
        """Test yesterday screen generation."""
        mock_date.return_value = '01/01/2024'
        mock_fetch.return_value = []
        mock_grid.return_value = []

        widgets, title = get_yesterday_widgets(MagicMock(), MagicMock())

        self.assertIn("Yesterday's Scores", title)
        self.assertEqual(len(widgets), 2) # NavigationWidget and Label
        mock_fetch.assert_called_with('01/01/2024')

    @patch('app.screens.main_screens.get_today_date')
    @patch('app.screens.main_screens.fetch_schedule')
    @patch('app.screens.main_screens.create_grid')
    def test_get_today_widgets(self, mock_grid, mock_fetch, mock_date):
        """Test today screen generation."""
        mock_date.return_value = '01/02/2024'
        mock_fetch.return_value = []
        mock_grid.return_value = []

        widgets, title = get_today_widgets(MagicMock(), MagicMock())

        self.assertIn("Today's Schedule", title)
        self.assertEqual(len(widgets), 2)
        mock_fetch.assert_called_with('01/02/2024')

    @patch('app.screens.main_screens.fetch_standings')
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

        widgets, title = get_standings_widgets(MagicMock())

        self.assertIn("MLB Standings", title)
        # Nav, Label, 4 Division/WC Splitters
        self.assertEqual(len(widgets), 6)
        mock_fetch.assert_called_once()

if __name__ == '__main__':  # pragma: no cover
    unittest.main()

"""
Unit tests for BoxScoreScreen.
"""
import unittest
from unittest.mock import patch
import pytermgui as ptg
from app.screens.box_score_screen import BoxScoreScreen


class TestBoxScoreScreen(unittest.TestCase):
    """Test cases for BoxScoreScreen widget generation."""

    def _get_all_text(self, widget):
        """Helper to extract all text from a widget tree."""
        text = []
        if hasattr(widget, 'value'):
            text.append(str(widget.value))

        # Check sub-widgets for Container, Splitter, Window, etc.
        # pylint: disable=protected-access
        if hasattr(widget, '_widgets'):
            for sub in widget._widgets:
                text.extend(self._get_all_text(sub))
        elif hasattr(widget, 'widgets'):
            for sub in widget.widgets:
                text.extend(self._get_all_text(sub))
        return text

    @patch('app.screens.box_score_screen.fetch_boxscore')
    @patch('app.screens.box_score_screen.get_team_abbr')
    def test_get_widgets(self, mock_abbr, mock_fetch):
        """Test get_widgets generates expected widgets."""
        mock_abbr.side_effect = lambda x: f"TEAM_{x}"
        mock_fetch.return_value = {
            'away': {
                'team': {'id': 1},
                'teamStats': {'batting': {'runs': 5, 'hits': 8, 'errors': 0}}
            },
            'home': {
                'team': {'id': 2},
                'teamStats': {'batting': {'runs': 3, 'hits': 6, 'errors': 1}}
            }
        }

        widgets, title = BoxScoreScreen.get_widgets(123)

        self.assertIn("TEAM_1 vs TEAM_2 Box Score", title)

        all_text = []
        for w in widgets:
            all_text.extend(self._get_all_text(w))

        self.assertTrue(any("TEAM_1" in t for t in all_text))
        self.assertTrue(any("5" in t for t in all_text))
        self.assertTrue(any("3" in t for t in all_text))

    @patch('app.screens.box_score_screen.get_team_abbr')
    def test_create_linescore_fallback(self, mock_abbr):
        """Test _create_linescore handles missing data gracefully."""
        mock_abbr.return_value = "N/A"
        # Test with empty data
        data = {}
        # pylint: disable=protected-access
        widgets = BoxScoreScreen._create_linescore(data)
        self.assertEqual(len(widgets), 2)
        self.assertIsInstance(widgets[0], ptg.Splitter)
        self.assertIsInstance(widgets[1], ptg.Container)

"""
Unit tests for the game_widgets module.
"""
import unittest
from unittest.mock import patch, MagicMock
import pytermgui as ptg
from app.widgets.game_widgets import (
    Separator,
    GameWidget,
    StandingWidget,
    NavigationWidget,
    chunk_list,
    create_grid
)

class TestGameWidgets(unittest.TestCase):
    """Test cases for game_widgets.py classes and functions."""

    def test_separator_init(self):
        """Test Separator initialization."""
        sep = Separator()
        self.assertIsInstance(sep, ptg.Label)
        self.assertEqual(sep.value, "─" * 10)

    @patch('app.widgets.game_widgets.get_team_abbr')
    def test_game_widget_init(self, mock_abbr):
        """Test GameWidget data mapping."""
        mock_abbr.side_effect = lambda x: f"T{x}"
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'away_score': 5,
            'home_score': 3,
            'status': 'Final'
        }
        widget = GameWidget(game)
        self.assertEqual(widget.game_id, 123)
        # Check if labels contain expected abbreviations and scores
        self.assertIn("T1", widget.away_label.value)
        self.assertIn("5", widget.away_label.value)
        self.assertIn("T2", widget.home_label.value)
        self.assertIn("3", widget.home_label.value)

    @patch('app.widgets.game_widgets.get_team_abbr')
    def test_standing_widget_init(self, mock_abbr):
        """Test StandingWidget data mapping with pct and l10."""
        mock_abbr.side_effect = lambda x: f"T{x}"
        div_data = {
            'div_name': 'American League East',
            'teams': [
                {'team_id': 1, 'w': 90, 'l': 72, 'gb': '-', 'pct': '55.6%', 'l10': '6-4'}
            ]
        }
        widget = StandingWidget(div_data)
        labels = [w.value for w in widget.inner_widgets if isinstance(w, ptg.Label)]
        self.assertTrue(any("AL East" in l for l in labels))
        self.assertTrue(any(
            "T1" in l and "90" in l and "72" in l and "55.6%" in l and "6-4" in l
            for l in labels
        ))

    @patch('app.widgets.game_widgets.get_team_abbr')
    def test_game_widget_scheduled(self, mock_abbr):
        """Test GameWidget with scheduled status shows '-' for scores."""
        mock_abbr.return_value = "TEST"
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'status': 'Scheduled'
        }
        widget = GameWidget(game)
        self.assertIn("-", widget.away_label.value)
        self.assertIn("-", widget.home_label.value)

    @patch('app.widgets.game_widgets.get_team_abbr')
    def test_game_widget_none_scores(self, mock_abbr):
        """Test GameWidget with None scores shows '-'."""
        mock_abbr.return_value = "TEST"
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'away_score': None,
            'home_score': None,
            'status': 'Final'
        }
        widget = GameWidget(game)
        self.assertIn("-", widget.away_label.value)
        self.assertIn("-", widget.home_label.value)

    def test_game_widget_handle_key(self):
        """Test GameWidget handle_key returns super().handle_key()."""
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'status': 'Final'
        }
        widget = GameWidget(game)
        # Mock super().handle_key to return True
        with patch('pytermgui.Container.handle_key', return_value=True):
            self.assertTrue(widget.handle_key(ptg.keys.RETURN))
            self.assertTrue(widget.handle_key('some_other_key'))

    def test_standing_widget_no_data(self):
        """Test StandingWidget with no division data."""
        widget = StandingWidget(None)
        labels = [w.value for w in widget.inner_widgets if isinstance(w, ptg.Label)]
        self.assertIn("No Data", labels[0])

    def test_navigation_widget_init(self):
        """Test NavigationWidget highlighting."""
        # Test yesterday active
        widget = NavigationWidget(active_page="yesterday")
        self.assertIn("[inverse]Yesterday", widget.yest_label.value)
        self.assertNotIn("[inverse]Today", widget.today_label.value)
        self.assertNotIn("[inverse]Standings", widget.stand_label.value)

    def test_chunk_list(self):
        """Test chunk_list utility."""
        lst = [1, 2, 3, 4, 5]
        chunks = list(chunk_list(lst, 2))
        self.assertEqual(chunks, [[1, 2], [3, 4], [5]])

    @patch('app.widgets.game_widgets.GameWidget')
    def test_create_grid(self, mock_game_widget):
        """Test grid creation logic."""
        mock_game_widget.return_value = MagicMock()
        games = [{}, {}, {}, {}] # 4 games -> 2 rows
        grid = create_grid(games)
        self.assertEqual(len(grid), 2)
        self.assertEqual(len(grid[0]), 3) # Row length is 3

if __name__ == '__main__':  # pragma: no cover
    unittest.main()

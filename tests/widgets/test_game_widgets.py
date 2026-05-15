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

    def _get_label_values(self, widget):
        """Helper to extract all label values from a widget's tree."""
        values = []
        if hasattr(widget, 'value'):
            values.append(widget.value)

        # Check for child widgets in Containers or Splitters
        # pylint: disable=protected-access
        if hasattr(widget, '_widgets'):
            for child in widget._widgets:
                values.extend(self._get_label_values(child))
        elif hasattr(widget, 'widgets'):
            for child in widget.widgets:
                values.extend(self._get_label_values(child))
        return values

    @patch('app.widgets.game_widgets.get_team_abbr')
    def test_game_widget_init(self, mock_abbr):
        """Test GameWidget data mapping with inning data."""
        mock_abbr.side_effect = lambda x: f"T{x}"
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'away_score': 5,
            'home_score': 3,
            'status': 'Final',
            'current_inning': 9,
            'inning_state': 'Top'
        }
        widget = GameWidget(game)
        self.assertEqual(widget.game_id, 123)

        values = self._get_label_values(widget)
        # Check for abbreviations and scores
        self.assertTrue(any("T1" in v and "5" in v for v in values))
        self.assertTrue(any("T2" in v and "3" in v for v in values))
        # Check inning label for Final game
        self.assertTrue(any("FINAL" in v for v in values))

    @patch('app.widgets.game_widgets.get_team_abbr')
    def test_game_widget_in_progress(self, mock_abbr):
        """Test GameWidget with in-progress inning data."""
        mock_abbr.return_value = "TEST"
        # Top of 5th
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'status': 'In Progress',
            'current_inning': 5,
            'inning_state': 'Top'
        }
        widget = GameWidget(game)
        values = self._get_label_values(widget)
        self.assertTrue(any("TOP 5" in v for v in values))

        # Bottom of 7th
        game['inning_state'] = 'Bottom'
        game['current_inning'] = 7
        widget = GameWidget(game)
        values = self._get_label_values(widget)
        self.assertTrue(any("BOT 7" in v for v in values))

    @patch('app.widgets.game_widgets.get_team_abbr')
    def test_game_widget_scheduled(self, mock_abbr):
        """Test GameWidget with scheduled status shows start time."""
        mock_abbr.return_value = "TEST"
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'status': 'Scheduled',
            'game_datetime': '2026-05-15T22:40:00Z'
        }
        widget = GameWidget(game)
        values = self._get_label_values(widget)

        # Check for '-' scores
        self.assertTrue(any("TEST" in v and "-" in v for v in values))
        # Check for time (should contain 'AM' or 'PM' and ':')
        self.assertTrue(any(":" in v and ("AM" in v or "PM" in v) for v in values))

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
        values = self._get_label_values(widget)
        self.assertTrue(any("-" in v for v in values))

    @patch('app.widgets.game_widgets.get_team_abbr')
    def test_game_widget_malformed_time(self, mock_abbr):
        """Test GameWidget with malformed game_datetime."""
        mock_abbr.return_value = "TEST"
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'status': 'Scheduled',
            'game_datetime': 'invalid-time'
        }
        widget = GameWidget(game)
        values = self._get_label_values(widget)
        # inning_text should be empty string
        self.assertTrue(all(v != "invalid-time" for v in values))

    @patch('app.widgets.game_widgets.get_team_abbr')
    def test_game_widget_in_progress_no_inning(self, mock_abbr):
        """Test GameWidget in-progress but with no inning data."""
        mock_abbr.return_value = "TEST"
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'status': 'In Progress',
            'current_inning': None,
            'inning_state': None
        }
        widget = GameWidget(game)
        values = self._get_label_values(widget)
        # Should not crash, and status should be empty
        self.assertTrue(any("TEST" in v for v in values))

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

    def test_game_widget_handle_key(self):
        """Test GameWidget handle_key returns super().handle_key()."""
        game = {
            'game_id': 123,
            'away_id': 1,
            'home_id': 2,
            'status': 'Final'
        }
        widget = GameWidget(game)
        # Test RETURN key to cover the branch
        widget.handle_key(ptg.keys.RETURN)
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

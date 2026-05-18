"""
Tests for box score navigation and screen transitions.
"""
import unittest
from unittest.mock import patch, MagicMock
import pytermgui as ptg
from app.mlb_cli import MLBApp
from app.widgets.game_widget import GameWidget

class TestBoxScoreNavigation(unittest.TestCase):
    """Test cases for navigating to and from the box score screen."""
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
            self.app.main_window.selectables = []

    @patch('app.mlb_cli.ptg.Window')
    def test_update_to_box_score(self, mock_window):
        """Test transitioning to the box score screen."""
        mock_win_instance = mock_window.return_value
        mock_win_instance.height = 10
        with patch('app.mlb_cli.BoxScoreScreen.get_widgets') as mock_get:
            mock_get.return_value = ([], "Box Score")
            self.app.update_to_box_score(123)
            self.assertEqual(self.app.state.active_page, "boxscore:123")

    def test_handle_back_from_box_score(self):
        """Test returning to the schedule screen from the box score."""
        self.app.state.active_page = "boxscore:123"
        with patch.object(self.app, 'update_to_schedule') as mock_update:
            self.app.handle_back()
            mock_update.assert_called_once()

    def test_handle_back_not_box_score(self):
        """Test handle_back does nothing if not on box score screen."""
        self.app.state.active_page = "schedule:05/17/2026"
        with patch.object(self.app, 'update_to_schedule') as mock_update:
            self.app.handle_back()
            mock_update.assert_not_called()

    def test_focus_first_game_in_schedule(self):
        """Test focusing the first GameWidget in the schedule."""
        # pylint: disable=protected-access
        mock_game = MagicMock(spec=GameWidget)
        self.app.main_window.selectables = [(mock_game, None)]

        self.app._focus_first_game_in_schedule()

        self.app.main_window.select.assert_called_once_with(0)
        self.assertEqual(self.app.manager.focused, mock_game)

    @patch('app.mlb_cli.ScheduleScreen.get_widgets')
    def test_update_to_schedule_passes_callback(self, mock_get):
        """Test update_to_schedule passes update_to_box_score as callback."""
        mock_get.return_value = ([], "Schedule")
        with patch.object(self.app, 'set_window_data'):
            self.app.update_to_schedule()
            mock_get.assert_called_once()
            _, kwargs = mock_get.call_args
            self.assertEqual(kwargs['on_game_selected'], self.app.update_to_box_score)

if __name__ == '__main__':
    unittest.main()

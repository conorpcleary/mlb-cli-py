"""
Unit tests for the main mlb_cli application.
"""
import unittest
from unittest.mock import patch, MagicMock
import pytermgui as ptg
from mlb_cli import MLBApp

class TestMLBApp(unittest.TestCase):
    """Test cases for the MLBApp class."""

    @patch('mlb_cli.fetch_teams')
    @patch('mlb_cli.ptg.WindowManager')
    def setUp(self, mock_manager, mock_fetch):
        """Initialize MLBApp with mocked WindowManager."""
        self.app = MLBApp()
        self.app.main_window = MagicMock(spec=ptg.Window)

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
        self.app.set_window_data([], "Title", "page1")
        self.assertEqual(self.app.active_page, "page1")

    @patch('mlb_cli.slide_transition')
    def test_set_window_data_transition(self, mock_transition):
        """Test set_window_data triggers slide_transition for subsequent calls."""
        self.app.is_initialized = True
        self.app.active_page = "page1"
        widgets = [ptg.Label("test")]
        
        self.app.set_window_data(widgets, "New Title", "page2")
        
        self.assertEqual(self.app.active_page, "page2")
        mock_transition.assert_called_once()

    @patch('mlb_cli.get_yesterday_widgets')
    def test_update_to_yesterday(self, mock_get):
        """Test transition to yesterday's scores."""
        mock_get.return_value = ([], "Yesterday")
        self.app.update_to_yesterday()
        self.assertEqual(self.app.active_page, "yesterday")

    @patch('mlb_cli.get_today_widgets')
    def test_update_to_today(self, mock_get):
        """Test transition to today's schedule."""
        mock_get.return_value = ([], "Today")
        self.app.update_to_today()
        self.assertEqual(self.app.active_page, "today")

    @patch('mlb_cli.get_standings_widgets')
    def test_update_to_standings(self, mock_get):
        """Test transition to standings."""
        mock_get.return_value = ([], "Standings")
        self.app.update_to_standings()
        self.assertEqual(self.app.active_page, "standings")

    def test_exit_app(self):
        """Test application exit."""
        self.app.exit_app()
        self.app.manager.stop.assert_called_once()

    @patch('mlb_cli.ptg.Window')
    def test_run(self, mock_window):
        """Test main run loop setup."""
        # Mock terminal height
        self.app.manager.terminal.height = 40
        
        # Mock run to exit immediately
        self.app.manager.run.side_effect = None
        
        with patch.object(self.app, 'update_to_yesterday'):
            self.app.run()
            
            self.app.manager.add.assert_called_once()
            self.app.update_to_yesterday.assert_called_once()
            self.app.manager.run.assert_called_once()

    @patch('mlb_cli.MLBApp')
    def test_main(self, mock_app_class):
        """Test the main() entry point."""
        mock_app_instance = mock_app_class.return_value
        from mlb_cli import main
        main()
        mock_app_class.assert_called_once()
        mock_app_instance.run.assert_called_once()

if __name__ == '__main__':  # pragma: no cover
    unittest.main()

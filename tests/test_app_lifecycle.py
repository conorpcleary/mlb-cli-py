"""
Unit tests for the application lifecycle of MLBApp.
"""
import unittest
from unittest.mock import patch, MagicMock
import pytermgui as ptg
from app.mlb_cli import MLBApp, main


class TestAppLifecycle(unittest.TestCase):
    """Test cases for the MLBApp lifecycle (init, run, exit)."""
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

    def test_init(self):
        """Test MLBApp initialization."""
        self.assertEqual(self.app.static_width, 80)
        self.assertFalse(self.app.is_initialized)
        self.assertIsNone(self.app.state.active_page)

    def test_set_window_data_initial(self):
        """Test initial call to set_window_data."""
        widgets = [ptg.Label("test")]
        self.app.set_window_data(widgets, "Title", "page1")

        self.assertTrue(self.app.is_initialized)
        self.assertEqual(self.app.state.active_page, "page1")
        self.app.main_window.set_widgets.assert_called_with(widgets)
        self.app.main_window.set_title.assert_called_with("Title")

    def test_set_window_data_same_page(self):
        """Test set_window_data with the same page name does nothing."""
        self.app.state.active_page = "page1"
        self.app.main_window.set_widgets.reset_mock()
        self.app.set_window_data([], "Title", "page1")
        self.app.main_window.set_widgets.assert_not_called()

    def test_set_window_data_same_page_with_callback(self):
        """Test set_window_data with the same page name and a callback."""
        self.app.state.active_page = "page1"
        mock_finish = MagicMock()
        self.app.set_window_data([], "Title", "page1", on_finish=mock_finish)
        mock_finish.assert_called_once()

    @patch('app.mlb_cli.slide_transition')
    def test_set_window_data_transition(self, mock_transition):
        """Test set_window_data triggers slide_transition for subsequent calls."""
        self.app.is_initialized = True
        self.app.state.active_page = "page1"
        widgets = [ptg.Label("test")]

        self.app.set_window_data(widgets, "New Title", "page2")

        self.assertEqual(self.app.state.active_page, "page2")
        mock_transition.assert_called_once()

    def test_exit_app(self):
        """Test application exit."""
        self.app.exit_app()
        self.app.manager.stop.assert_called_once()

    @patch('app.mlb_cli.ptg.Window')
    def test_run(self, _mock_window):
        """Test main run loop setup."""
        # Mock run to exit immediately
        self.app.manager.run.side_effect = None

        with patch.object(self.app, 'update_to_calendar') as mock_update:
            self.app.run()

            self.app.manager.add.assert_called_once()
            mock_update.assert_called_once()
            self.app.manager.run.assert_called_once()

    @patch('app.mlb_cli.MLBApp')
    def test_main(self, mock_app_class):
        """Test the main() entry point."""
        mock_app_instance = mock_app_class.return_value
        main()
        mock_app_class.assert_called_once()
        mock_app_instance.run.assert_called_once()


if __name__ == '__main__':
    unittest.main()

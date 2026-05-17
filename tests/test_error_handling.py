"""
Unit tests for the error handling logic in MLBApp.
"""
import unittest
from unittest.mock import patch, MagicMock
import pytermgui as ptg
from app.mlb_cli import MLBApp
from app.exceptions import APIError
from app.screens import ErrorScreen


class TestErrorHandling(unittest.TestCase):
    """Test cases for the global exception handling and error screen."""

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

    @patch('app.screens.ErrorScreen.get_widgets')
    def test_handle_errors_decorator_api_error(self, mock_get_error):
        """Test that APIError triggers ErrorScreen."""
        mock_get_error.return_value = ([], "Error Title")

        @MLBApp.handle_errors
        def failing_method(app_instance):
            raise APIError("API failure")

        with patch.object(self.app, 'set_window_data') as mock_set:
            result = failing_method(self.app)
            self.assertFalse(result)
            mock_get_error.assert_called_with("API failure")
            mock_set.assert_called_with([], "Error Title", "error")

    @patch('app.screens.ErrorScreen.get_widgets')
    def test_handle_errors_decorator_generic_exception(self, mock_get_error):
        """Test that generic Exception triggers user-friendly ErrorScreen message."""
        mock_get_error.return_value = ([], "Error Title")

        @MLBApp.handle_errors
        def crashing_method(app_instance):
            raise RuntimeError("Unexpected crash")

        with patch.object(self.app, 'set_window_data') as mock_set:
            result = crashing_method(self.app)
            self.assertFalse(result)
            # Should NOT show the internal message "Unexpected crash" but a generic one
            mock_get_error.assert_called_with("An unexpected error occurred")
            mock_set.assert_called_with([], "Error Title", "error")

    def test_error_screen_widgets(self):
        """Test that ErrorScreen returns the expected number of widgets."""
        widgets, title = ErrorScreen.get_widgets("Test Error")
        self.assertEqual(title, "[red]Application Error[/]")
        # NavigationWidget + Label x 10
        self.assertEqual(len(widgets), 11)
        # Check if the error message is present in the labels
        found = False
        for w in widgets:
            if hasattr(w, 'value') and "Test Error" in w.value:
                found = True
                break
        self.assertTrue(found)

if __name__ == '__main__':
    unittest.main()

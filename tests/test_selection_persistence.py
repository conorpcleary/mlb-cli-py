"""
Test to verify that MLBWindow preserves selection on blur.
"""
import unittest
import pytermgui as ptg
from app.mlb_cli import MLBWindow


class TestSelectionPersistence(unittest.TestCase):
    """Test cases for verifying selection persistence on MLBWindow blur."""

    def test_mlb_window_preserves_selection_on_blur(self):
        """Verify that MLBWindow.blur() does not deselect content."""
        window = MLBWindow()
        btn = ptg.Button("Test")
        window += btn
        window.select(0)

        self.assertEqual(window.selected, btn)

        # Blur the window
        window.blur()

        # Selection should persist
        self.assertEqual(window.selected, btn)
        self.assertFalse(window.has_focus)

    def test_standard_window_deselects_on_blur(self):
        """Verify standard ptg.Window.blur() DOES deselect (baseline check)."""
        window = ptg.Window()
        btn = ptg.Button("Test")
        window += btn
        window.select(0)

        self.assertEqual(window.selected, btn)

        # Blur the window
        window.blur()

        # Selection should be None
        self.assertIsNone(window.selected)


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for the animations module.
"""
import unittest
from unittest.mock import MagicMock, patch
import pytermgui as ptg
from app.widgets.animations import slide_transition

class TestAnimations(unittest.TestCase):
    """Test cases for animations.py functions."""

    @patch('pytermgui.animator.animate_float')
    def test_slide_transition(self, mock_animate):
        """Test slide_transition starts the animation and handles callbacks."""
        mock_window = MagicMock(spec=ptg.Window)
        mock_window.width = 80
        mock_window.height = 20
        mock_window.pos = (10, 5)

        mock_manager = MagicMock(spec=ptg.WindowManager)
        mock_manager.terminal.width = 100
        mock_manager.terminal.height = 30

        widgets = [MagicMock()]
        title = "New Title"

        # Call slide_transition
        slide_transition(mock_window, mock_manager, widgets, title)

        # 1. Verify first animation call (Slide-out)
        self.assertEqual(mock_animate.call_count, 1)
        _, kwargs = mock_animate.call_args
        self.assertEqual(kwargs['duration'], 290)
        self.assertEqual(kwargs['direction'], ptg.animations.Direction.FORWARD)

        # 2. Test on_finish for slide-out
        on_finish = kwargs['on_finish']
        mock_animate.reset_mock() # Reset to capture slide-in call

        on_finish(None)

        # Verify window content update
        mock_window.set_widgets.assert_called_with(widgets)
        mock_window.set_title.assert_called_with(title)
        self.assertEqual(mock_window.width, 80)
        self.assertEqual(mock_window.height, 20)
        self.assertEqual(mock_window.styles.border, "green")
        self.assertEqual(mock_window.styles.corner, "green")

        # Verify second animation call (Slide-in)
        self.assertEqual(mock_animate.call_count, 1)
        _, kwargs_in = mock_animate.call_args
        self.assertEqual(kwargs_in['direction'], ptg.animations.Direction.BACKWARD)

        # Test on_step for slide-in
        on_step_in = kwargs_in['on_step']
        mock_anim_in = MagicMock()
        mock_anim_in.state = 0.2
        # curr_x = int(10 + (100 - 10) * 0.2) = 10 + 18 = 28
        on_step_in(mock_anim_in)
        self.assertEqual(mock_window.pos, (28, 5))

if __name__ == '__main__':  # pragma: no cover
    unittest.main()

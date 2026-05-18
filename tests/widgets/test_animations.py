"""
Unit tests for animation utilities.
"""
import unittest
from unittest.mock import patch, MagicMock
import pytermgui as ptg
from app.widgets.animations import slide_transition


class TestAnimations(unittest.TestCase):
    """Test cases for animation functions."""
    # pylint: disable=duplicate-code

    @patch('pytermgui.animator.animate_float')
    def test_slide_transition_execution(self, mock_animate):
        """Test slide_transition and its internal callbacks."""
        window = MagicMock(spec=ptg.Window)
        window.width = 10
        window.height = 5
        window.pos = (0, 0)
        manager = MagicMock(spec=ptg.WindowManager)
        manager.terminal.width = 100

        on_finish = MagicMock()

        # We need to simulate the animation flow.
        # slide_transition calls animate_float for slide-out.
        # on_slide_out_finish starts slide-in.
        # on_slide_in_finish calls on_finish.

        def mock_animate_float(duration, direction, on_finish=None, on_step=None):
            # pylint: disable=unused-argument
            # Simulate step if provided
            if on_step:
                mock_anim = MagicMock()
                mock_anim.state = 0.5
                on_step(mock_anim)

            # Simulate finish
            if on_finish:
                on_finish(MagicMock())

        mock_animate.side_effect = mock_animate_float

        slide_transition(window, manager, [], "Title", on_finish=on_finish)

        # Verify window properties were updated
        window.set_widgets.assert_called_once()
        window.set_title.assert_called_once_with("Title")
        on_finish.assert_called_once()

        # Verify window.pos was updated during on_step
        self.assertNotEqual(window.pos, (0, 0))

    @patch('pytermgui.animator.animate_float')
    def test_slide_transition_no_on_finish(self, mock_animate):
        """Test slide_transition without on_finish callback."""
        window = MagicMock(spec=ptg.Window)
        window.width = 10
        window.height = 5
        window.pos = (0, 0)
        manager = MagicMock()
        manager.terminal.width = 100

        def mock_animate_float(duration, direction, on_finish=None, on_step=None):
            # pylint: disable=unused-argument
            if on_finish:
                on_finish(MagicMock())

        mock_animate.side_effect = mock_animate_float

        # Should not crash
        slide_transition(window, manager, [], "Title")
        mock_animate.assert_called()

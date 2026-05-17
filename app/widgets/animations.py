"""
Animation utilities for the MLB CLI application.
Provides functions for sliding windows and other transitions.
"""
import pytermgui as ptg
from pytermgui.animations import Direction


# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
def slide_transition(window, manager, widgets, title, duration=290, on_finish=None,
                     new_width=None, new_height=None):
    """
    Performs a slide-out and slide-in transition for a window.

    Args:
        window (ptg.Window): The window to animate.
        manager (ptg.WindowManager): The manager containing the window.
        widgets (list): The new widgets to set after sliding out.
        title (str): The new title to set after sliding out.
        duration (int): Duration of each slide stage in milliseconds.
        on_finish (callable, optional): Callback to run when the entire transition finishes.
        new_width (int, optional): The target width for the window.
        new_height (int, optional): The target height for the window.
    """
    # Use provided dimensions or fallback to current ones
    target_width = new_width if new_width is not None else window.width
    target_height = new_height if new_height is not None else window.height

    # Calculate starting position for slide-in (centered)
    final_target_x = (manager.terminal.width - target_width) // 2
    _, start_y = window.pos
    off_screen_right = manager.terminal.width

    def slide_step(anim, off_x, current_target_x):
        """Updates the window position based on animation state and off-screen target."""
        curr_x = int(current_target_x + (off_x - current_target_x) * anim.state)
        window.pos = (curr_x, start_y)
        return False

    def on_slide_in_finish(_):
        """Runs the external on_finish callback if provided."""
        if on_finish:
            on_finish()

    def on_slide_out_finish(_):
        """Updates window content and starts the slide-in animation using Direction.BACKWARD."""
        window.set_widgets(widgets)
        window.set_title(title)
        window.width = target_width
        window.height = target_height
        window.styles.border = "green"
        window.styles.corner = "green"

        ptg.animator.animate_float(
            duration=duration,
            direction=Direction.BACKWARD,
            on_step=lambda anim: slide_step(anim, off_screen_right, final_target_x),
            on_finish=on_slide_in_finish
        )

    # Start the slide-out animation using Direction.FORWARD
    ptg.animator.animate_float(
        duration=duration,
        direction=Direction.FORWARD,
        on_finish=on_slide_out_finish
    )

"""
Animation utilities for the MLB CLI application.
Provides functions for sliding windows and other transitions.
"""
import pytermgui as ptg
from pytermgui.animations import Direction


# pylint: disable=too-many-arguments,too-many-positional-arguments
def slide_transition(window, manager, widgets, title, duration=290, on_finish=None):
    """
    Performs a slide-out and slide-in transition for a window.

    Args:
        window (ptg.Window): The window to animate.
        manager (ptg.WindowManager): The manager containing the window.
        widgets (list): The new widgets to set after sliding out.
        title (str): The new title to set after sliding out.
        duration (int): Duration of each slide stage in milliseconds.
        on_finish (callable, optional): Callback to run when the entire transition finishes.
    """
    static_width = window.width
    static_height = window.height

    target_x = (manager.terminal.width - static_width) // 2
    _, start_y = window.pos
    off_screen_right = manager.terminal.width

    def slide_step(anim, off_x):
        """Updates the window position based on animation state and off-screen target."""
        curr_x = int(target_x + (off_x - target_x) * anim.state)
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
        window.width = static_width
        window.height = static_height
        window.styles.border = "green"
        window.styles.corner = "green"

        ptg.animator.animate_float(
            duration=duration,
            direction=Direction.BACKWARD,
            on_step=lambda anim: slide_step(anim, off_screen_right),
            on_finish=on_slide_in_finish
        )

    # Start the slide-out animation using Direction.FORWARD
    ptg.animator.animate_float(
        duration=duration,
        direction=Direction.FORWARD,
        on_finish=on_slide_out_finish
    )

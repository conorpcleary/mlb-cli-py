"""
Animation utilities for the MLB CLI application.
Provides functions for sliding windows and other transitions.
"""
import pytermgui as ptg


def slide_transition(window, manager, widgets, title, duration=250):
    """
    Performs a slide-out and slide-in transition for a window.

    Args:
        window (ptg.Window): The window to animate.
        manager (ptg.WindowManager): The manager containing the window.
        widgets (list): The new widgets to set after sliding out.
        title (str): The new title to set after sliding out.
        duration (int): Duration of each slide stage in milliseconds.
    """
    static_width = window.width
    static_height = window.height

    target_x = (manager.terminal.width - static_width) // 2
    start_x, start_y = window.pos
    off_screen_left = -static_width
    off_screen_right = manager.terminal.width

    def slide_out_step(anim):
        """Steps the window towards the left off-screen position."""
        curr_x = int(start_x + (off_screen_left - start_x) * anim.state)
        window.pos = (curr_x, start_y)
        return False

    def slide_in_step(anim):
        """Steps the window from the right off-screen position to the center."""
        curr_x = int(off_screen_right + (target_x - off_screen_right) * anim.state)
        window.pos = (curr_x, start_y)
        return False

    def on_slide_out_finish(_):
        """Updates window content and starts the slide-in animation."""
        window.set_widgets(widgets)
        window.set_title(title)
        window.width = static_width
        window.height = static_height
        window.styles.border = "green"
        window.styles.corner = "green"

        ptg.animator.animate_float(
            duration=duration,
            on_step=slide_in_step
        )

    # Start the slide-out animation
    ptg.animator.animate_float(
        duration=duration,
        on_step=slide_out_step,
        on_finish=on_slide_out_finish
    )

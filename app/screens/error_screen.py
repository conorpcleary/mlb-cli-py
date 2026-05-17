"""
Error screen for the MLB CLI application.
Displays error messages and recovery instructions.
"""
import pytermgui as ptg
from app.widgets import NavigationWidget


class ErrorScreen:
    # pylint: disable=too-few-public-methods
    """
    Screen class for displaying error messages.
    """

    @staticmethod
    def get_widgets(error_message):
        """
        Generates the widget list and title for an error message.

        Args:
            error_message (str): The error message to display.

        Returns:
            tuple: (list of widgets, title string)
        """
        widgets = [
            NavigationWidget(), # Default nav for recovery
            ptg.Label(""),
            ptg.Label("[bold red]ERROR[/]", parent_align=ptg.HorizontalAlignment.CENTER),
            ptg.Label(""),
            ptg.Label(f"[italic]{error_message}[/]", parent_align=ptg.HorizontalAlignment.CENTER),
            ptg.Label(""),
            ptg.Label("Please check your connection or try again later.",
                      parent_align=ptg.HorizontalAlignment.CENTER),
            ptg.Label(""),
            ptg.Label("Press [bold cyan]t[/] to return to Today's schedule.",
                      parent_align=ptg.HorizontalAlignment.CENTER),
            ptg.Label("Press [bold cyan]ESC[/] to exit.",
                      parent_align=ptg.HorizontalAlignment.CENTER),
            ptg.Label(""),
        ]
        return widgets, "[red]Application Error[/]"

"""
Schedule screen for the MLB CLI application.
"""
import pytermgui as ptg
from app.widgets import create_grid, NavigationWidget
from app.models.data_service import fetch_schedule


class ScheduleScreen:
    # pylint: disable=too-few-public-methods
    """
    Screen class for displaying the MLB schedule.
    """

    @staticmethod
    def get_widgets(date_str, on_game_selected=None):
        """
        Generates the widget list and title for a specific date's schedule.

        Args:
            date_str (str): The date string in MM/DD/YYYY format.
            on_game_selected (callable, optional): Callback when a game is selected.

        Returns:
            tuple: (list of widgets, title string)
        """
        games = fetch_schedule(date_str)

        widgets = [
            NavigationWidget(active_page="schedule"),
            ptg.Label(f"[bold]MLB Schedule - {date_str}[/]"),
            *create_grid(games, on_game_selected=on_game_selected),
        ]
        return widgets, f"[green]MLB Schedule - {date_str}[/]"

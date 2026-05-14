"""
Screen definitions for the MLB CLI application.
Contains functions that return lists of widgets and titles for different application views.
"""
import pytermgui as ptg
from app.widgets.game_widgets import create_grid, StandingWidget, NavigationWidget
from app.models.data_service import (
    fetch_schedule, 
    get_yesterday_date, 
    get_today_date, 
    fetch_standings
)

def get_yesterday_widgets(on_switch_today, on_switch_standings):
    """
    Generates the widget list and title for the 'Yesterday's Scores' screen.

    Args:
        on_switch_today (callable): Callback to switch to the 'Today' screen.
        on_switch_standings (callable): Callback to switch to the 'Standings' screen.

    Returns:
        tuple: (list of widgets, title string)
    """
    date_str = get_yesterday_date()
    games = fetch_schedule(date_str)

    widgets = [
        NavigationWidget(active_page="yesterday"),
        ptg.Label(f"[bold]MLB Scores - {date_str}[/]"),
        *create_grid(games),
    ]
    return widgets, "[green]Yesterday's Scores[/]"


def get_today_widgets(on_switch_yesterday, on_switch_standings):
    """
    Generates the widget list and title for the 'Today's Schedule' screen.

    Args:
        on_switch_yesterday (callable): Callback to switch to the 'Yesterday' screen.
        on_switch_standings (callable): Callback to switch to the 'Standings' screen.

    Returns:
        tuple: (list of widgets, title string)
    """
    date_str = get_today_date()
    games = fetch_schedule(date_str)

    widgets = [
        NavigationWidget(active_page="today"),
        ptg.Label(f"[bold]MLB Schedule - {date_str}[/]"),
        *create_grid(games),
    ]
    return widgets, "[green]Today's Schedule[/]"


def get_standings_widgets(on_switch_yesterday):
    """
    Generates the widget list and title for the 'MLB Standings' screen.

    Args:
        on_switch_yesterday (callable): Callback to return to the scores view.

    Returns:
        tuple: (list of widgets, title string)
    """
    al_divs, nl_divs = fetch_standings()

    widgets = [
        NavigationWidget(active_page="standings"),
        ptg.Label("[bold]MLB Standings[/]"),
        # AL Row
        tuple(StandingWidget(d) for d in al_divs),
        # NL Row
        tuple(StandingWidget(d) for d in nl_divs),
    ]
    return widgets, "[green]MLB Standings[/]"

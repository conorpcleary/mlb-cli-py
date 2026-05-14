import pytermgui as ptg
from app.widgets.game_widgets import Separator, create_grid, StandingWidget
from app.models.data_service import fetch_schedule, get_yesterday_date, get_today_date, fetch_standings

def get_yesterday_widgets(on_switch_today, on_switch_standings):
    date_str = get_yesterday_date()
    games = fetch_schedule(date_str)
    
    widgets = [
        ptg.Label(f"[bold]MLB Scores - {date_str}[/]"),
        Separator(),
        *create_grid(games),
        Separator(),
        ptg.Splitter(
            ptg.Button("Show Today's Schedule", on_switch_today),
            ptg.Button("Show Standings", on_switch_standings)
        )
    ]
    return widgets, "[green]Yesterday's Scores[/]"

def get_today_widgets(on_switch_yesterday, on_switch_standings):
    date_str = get_today_date()
    games = fetch_schedule(date_str)
    
    widgets = [
        ptg.Label(f"[bold]MLB Schedule - {date_str}[/]"),
        Separator(),
        *create_grid(games),
        Separator(),
        ptg.Splitter(
            ptg.Button("Show Yesterday's Scores", on_switch_yesterday),
            ptg.Button("Show Standings", on_switch_standings)
        )
    ]
    return widgets, "[green]Today's Schedule[/]"

def get_standings_widgets(on_switch_yesterday):
    al_divs, nl_divs = fetch_standings()
    
    widgets = [
        ptg.Label("[bold]MLB Standings[/]"),
        Separator(),
        # AL Row
        tuple(StandingWidget(d) for d in al_divs),
        # NL Row
        tuple(StandingWidget(d) for d in nl_divs),
        Separator(),
        ptg.Button("Back to Scores", on_switch_yesterday)
    ]
    return widgets, "[green]MLB Standings[/]"

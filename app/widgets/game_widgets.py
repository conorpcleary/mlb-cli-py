"""
Custom widgets and UI components for the MLB CLI application.
Includes widgets for games, standings, navigation, and general layout.
"""
import pytermgui as ptg
from app.models.data_service import get_team_abbr


class Separator(ptg.Label):
    """A simple horizontal line separator widget."""
    def __init__(self, **kwargs):
        super().__init__("─" * 10, **kwargs)


class GameWidget(ptg.Container):
    """
    A container widget displaying the score and teams for a single MLB game.
    """
    def __init__(self, game, **kwargs):
        """
        Initializes the GameWidget with game data.

        Args:
            game (dict): Dictionary containing game details (teams, scores, status).
            **kwargs: Additional arguments for ptg.Container.
        """
        super().__init__(**kwargs)
        self.game_id = game['game_id']
        self._selectables_length = 1

        away_abbr = get_team_abbr(game['away_id'])
        home_abbr = get_team_abbr(game['home_id'])

        # Determine scores
        status = game.get('status', '')
        if status in ['Scheduled', 'Preview', 'Pre-Game']:
            away_score = "-"
            home_score = "-"
        else:
            away_score = game.get('away_score', "-")
            home_score = game.get('home_score', "-")
            if away_score is None:
                away_score = "-"
            if home_score is None:
                home_score = "-"

        self.set_widgets([
            ptg.Label(f"[bold]{away_abbr:3}[/] {away_score:>2}"),
            ptg.Label(f"[bold]{home_abbr:3}[/] {home_score:>2}"),
        ])
        self.border = ptg.boxes.SINGLE

    def handle_key(self, key):
        """
        Handles key events for the widget.

        Args:
            key (str): The key that was pressed.
        """
        if key == ptg.keys.RETURN:
            # Future: show box score
            pass
        return super().handle_key(key)


class StandingWidget(ptg.Container):
    """
    A container widget displaying the standings for a specific MLB division.
    """
    def __init__(self, division_data, **kwargs):
        """
        Initializes the StandingWidget with division data.

        Args:
            division_data (dict): Dictionary containing division name and team records.
            **kwargs: Additional arguments for ptg.Container.
        """
        super().__init__(**kwargs)
        if not division_data:
            self.set_widgets([ptg.Label("No Data")])
            return

        self._selectables_length = 1
        self.border = ptg.boxes.SINGLE

        name = division_data.get('div_name', 'Unknown')
        # Replace full league names with abbreviations
        name = name.replace(
            "American League",
            "AL").replace(
            "National League",
            "NL")

        widgets = [ptg.Label(f"[bold]{name}[/]")]
        widgets.append(ptg.Label("TM    W   L   GB"))

        for team in division_data.get('teams', []):
            # Use team abbreviation instead of full name
            abbr = get_team_abbr(team['team_id']).ljust(4)
            w = str(team['w']).rjust(3)
            l = str(team['l']).rjust(3)
            gb = str(team['gb']).rjust(4)
            widgets.append(ptg.Label(f"{abbr} {w} {l} {gb}"))

        self.set_widgets(widgets)


class NavigationWidget(ptg.Container):
    """
    A persistent navigation bar widget shown at the top of every screen.
    Displays available pages and their hotkeys, highlighting the active one.
    """
    def __init__(self, active_page=None, **kwargs):
        """
        Initializes the NavigationWidget.

        Args:
            active_page (str, optional): The name of the currently active screen.
            **kwargs: Additional arguments for ptg.Container.
        """
        super().__init__(**kwargs)
        self.border = ptg.boxes.EMPTY

        yest_style = "inverse" if active_page == "yesterday" else ""
        today_style = "inverse" if active_page == "today" else ""
        stand_style = "inverse" if active_page == "standings" else ""

        self.set_widgets([
            ptg.Splitter(
                ptg.Label(f"[{yest_style}]Yesterday[/] [bold][cyan][[/]",
                          parent_align=ptg.HorizontalAlignment.CENTER),
                ptg.Label(f"[{today_style}]Today[/] [bold][cyan]][/]",
                          parent_align=ptg.HorizontalAlignment.CENTER),
                ptg.Label(f"[{stand_style}]Standings[/] [bold][cyan]s[/]",
                          parent_align=ptg.HorizontalAlignment.CENTER),
            ),
            ptg.Label("─" * 60, parent_align=ptg.HorizontalAlignment.CENTER)
        ])


def chunk_list(lst, n):
    """
    Yields successive n-sized chunks from a list.

    Args:
        lst (list): The list to chunk.
        n (int): The size of each chunk.
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def create_grid(games):
    """
    Creates a grid layout of GameWidgets from a list of games.

    Args:
        games (list): List of game data dictionaries.

    Returns:
        list: A list of tuples, each representing a row of widgets for the grid.
    """
    grid_rows = []
    for game_group in chunk_list(games, 3):
        widgets = [GameWidget(game) for game in game_group]
        # Fill empty slots if less than 3 games in row
        while len(widgets) < 3:
            widgets.append(ptg.Label(""))
        grid_rows.append(tuple(widgets))
    return grid_rows

"""
Game widget for the MLB CLI application.
"""
from datetime import datetime, timezone
import pytermgui as ptg
from app.models.data_service import get_team_abbr


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

        status = game.get('status', '')
        away_score, home_score = self._get_scores(game, status)
        inning_text = self._get_inning_text(game, status)

        self.away_info, self.home_info = self._create_rows(
            (away_abbr, away_score),
            (home_abbr, home_score),
            inning_text
        )

        self.set_widgets([self.away_info, self.home_info])
        self.border = ptg.boxes.SINGLE

    def _get_scores(self, game, status):
        """Determines the away and home scores based on game status."""
        if status in ['Scheduled', 'Preview', 'Pre-Game']:
            return "-", "-"

        away_score = game.get('away_score', "-")
        home_score = game.get('home_score', "-")
        return (str(away_score) if away_score is not None else "-",
                str(home_score) if home_score is not None else "-")

    def _get_inning_text(self, game, status):
        """Formats the inning or start time text."""
        if status in ['Scheduled', 'Preview', 'Pre-Game']:
            try:
                dt_naive = datetime.strptime(game['game_datetime'], '%Y-%m-%dT%H:%M:%SZ')
                dt_aware = dt_naive.replace(tzinfo=timezone.utc)
                return dt_aware.astimezone().strftime('%-I:%M %p')
            except (ValueError, KeyError, TypeError):
                return ""

        if status == 'Final':
            return "FINAL"

        inning_val = game.get('current_inning')
        inning_state = game.get('inning_state', '')
        if inning_val:
            prefix = ""
            if inning_state.lower().startswith('top'):
                prefix = "TOP"
            elif inning_state.lower().startswith('bottom'):
                prefix = "BOT"
            return f"{prefix} {inning_val}"

        return ""

    def _create_rows(self, away_data, home_data, inning_text):
        """Creates the splitter rows for away and home teams."""
        away_abbr, away_score = away_data
        home_abbr, home_score = home_data

        away_row = ptg.Splitter(
            ptg.Label(f"[bold]{away_abbr:3}[/] {away_score:>2}"),
            ptg.Label("", parent_align=ptg.HorizontalAlignment.RIGHT)
        )

        home_row = ptg.Splitter(
            ptg.Label(f"[bold]{home_abbr:3}[/] {home_score:>2}"),
            ptg.Label(f"[italic]{inning_text}[/]", parent_align=ptg.HorizontalAlignment.CENTER)
        )
        return away_row, home_row

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

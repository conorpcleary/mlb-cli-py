"""
Box score screen for the MLB CLI application.
"""
import pytermgui as ptg
from app.models.data_service import fetch_boxscore, get_team_abbr
from app.widgets import NavigationWidget


class BoxScoreScreen:
    # pylint: disable=too-few-public-methods
    """
    Screen class for displaying a detailed game box score.
    """

    @staticmethod
    def get_widgets(game_id):
        """
        Generates the widget list and title for a specific game's box score.

        Args:
            game_id (int): The ID of the game.

        Returns:
            tuple: (list of widgets, title string)
        """
        data = fetch_boxscore(game_id)

        # Extract basic info
        away_team = data.get('away', {}).get('team', {})
        home_team = data.get('home', {}).get('team', {})
        away_abbr = get_team_abbr(away_team.get('id', 0))
        home_abbr = get_team_abbr(home_team.get('id', 0))

        title_label = ptg.Label(
            f"[bold]{away_abbr} vs {home_abbr} Box Score[/]",
            parent_align=ptg.HorizontalAlignment.CENTER
        )
        widgets = [
            NavigationWidget(active_page="boxscore"),
            title_label,
            ptg.Label(""),
        ]

        # Linescore
        linescore_widgets = BoxScoreScreen._create_linescore(data)
        widgets.extend(linescore_widgets)

        widgets.append(ptg.Label(""))
        back_label = ptg.Label(
            "[italic]Press 'q' to return to schedule[/]",
            parent_align=ptg.HorizontalAlignment.CENTER
        )
        widgets.append(back_label)

        return widgets, f"[green]{away_abbr} vs {home_abbr} Box Score[/]"

    @staticmethod
    def _create_linescore(data):
        """Creates the linescore table."""
        away_stats = data.get('away', {}).get('teamStats', {}).get('batting', {})
        home_stats = data.get('home', {}).get('teamStats', {}).get('batting', {})

        away_abbr = get_team_abbr(data.get('away', {}).get('team', {}).get('id', 0))
        home_abbr = get_team_abbr(data.get('home', {}).get('team', {}).get('id', 0))

        header = ptg.Splitter(
            ptg.Label("Team", width=10),
            ptg.Label("R", width=4),
            ptg.Label("H", width=4),
            ptg.Label("E", width=4),
        )

        away_row = ptg.Splitter(
            ptg.Label(f"[bold]{away_abbr:10}[/]"),
            ptg.Label(f"{away_stats.get('runs', 0):>2}", width=4),
            ptg.Label(f"{away_stats.get('hits', 0):>2}", width=4),
            ptg.Label(f"{away_stats.get('errors', 0):>2}", width=4),
        )

        home_row = ptg.Splitter(
            ptg.Label(f"[bold]{home_abbr:10}[/]"),
            ptg.Label(f"{home_stats.get('runs', 0):>2}", width=4),
            ptg.Label(f"{home_stats.get('hits', 0):>2}", width=4),
            ptg.Label(f"{home_stats.get('errors', 0):>2}", width=4),
        )

        return [header, ptg.Container(away_row, home_row, border=ptg.boxes.SINGLE)]

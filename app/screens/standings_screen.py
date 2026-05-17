"""
Standings screen for the MLB CLI application.
"""
import pytermgui as ptg
from app.widgets import StandingWidget, NavigationWidget
from app.models.data_service import fetch_standings


class StandingsScreen:
    # pylint: disable=too-few-public-methods
    """
    Screen class for displaying the MLB standings.
    """

    @staticmethod
    def get_widgets():
        """
        Generates the widget list and title for the 'MLB Standings' screen.

        Returns:
            tuple: (list of widgets, title string)
        """
        al_divs, nl_divs, al_wc, nl_wc = fetch_standings()

        # Define row structure with weights to ensure uniform width
        # 2 columns for divisions, centered 1 column (using padding) for Wild Cards
        widgets = [
            NavigationWidget(active_page="standings"),
            ptg.Label("[bold]MLB Standings[/]"),
            # East Row
            ptg.Splitter(StandingWidget(al_divs[0]), StandingWidget(nl_divs[0])),
            # Central Row
            ptg.Splitter(StandingWidget(al_divs[1]), StandingWidget(nl_divs[1])),
            # West Row
            ptg.Splitter(StandingWidget(al_divs[2]), StandingWidget(nl_divs[2])),
            # Wild Card Row (AL and NL)
            ptg.Splitter(StandingWidget(al_wc), StandingWidget(nl_wc)),
        ]
        return widgets, "[green]MLB Standings[/]"

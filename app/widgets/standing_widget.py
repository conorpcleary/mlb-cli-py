"""
Standing widget for the MLB CLI application.
"""
import pytermgui as ptg
from app.models.data_service import get_team_abbr


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
            self.inner_widgets = [ptg.Label("No Data")]
            self.set_widgets(self.inner_widgets)
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
        widgets.append(self._create_header())

        for team in division_data.get('teams', []):
            widgets.append(self._create_team_row(team))

        self.set_widgets(widgets)
        self.inner_widgets = widgets

    def _create_header(self):
        """Creates the header row for the standings."""
        tm_lbl = "TM".ljust(4)
        w_lbl = "W".rjust(3)
        l_lbl = "L".rjust(3)
        gb_lbl = "GB".rjust(4)
        pct_lbl = "PCT".rjust(6)
        l10_lbl = "L10".rjust(6)
        return ptg.Label(f"[bold]{tm_lbl} {w_lbl} {l_lbl} {gb_lbl} {pct_lbl} {l10_lbl}[/]")

    def _create_team_row(self, team):
        """Creates a data row for a single team."""
        # Use team abbreviation instead of full name
        abbr = get_team_abbr(team['team_id']).ljust(4)
        w = str(team['w']).rjust(3)
        l = str(team['l']).rjust(3)
        gb = str(team['gb']).rjust(4)
        pct = str(team['pct']).rjust(6)
        l10 = str(team['l10']).rjust(6)
        return ptg.Label(f"{abbr} {w} {l} {gb} {pct} {l10}")

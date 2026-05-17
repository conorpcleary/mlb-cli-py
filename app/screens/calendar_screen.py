"""
Calendar screen for the MLB CLI application.
"""
import calendar
import pytermgui as ptg
from app.widgets import NavigationWidget, CalendarWidget


class CalendarScreen:
    # pylint: disable=too-few-public-methods
    """
    Screen class for displaying the MLB calendar.
    """

    @staticmethod
    def get_widgets(year, months, on_date_selected, selected_date=None):
        """
        Generates the widget list and title for the calendar view showing multiple months.

        Args:
            year (int): Year to display.
            months (list): List of month integers to display.
            on_date_selected (callable): Callback for date selection.
            selected_date (datetime, optional): The currently selected date for highlighting.

        Returns:
            tuple: (list of widgets, title string)
        """
        month_widgets = []
        month_names = []

        for month in months:
            name = calendar.month_name[month]
            month_names.append(name)

            selected_day = None
            if selected_date and selected_date.year == year and \
               selected_date.month == month:
                selected_day = selected_date.day

            container = ptg.Container(
                ptg.Label(f"[bold]{name}[/]", parent_align=ptg.HorizontalAlignment.CENTER),
                CalendarWidget(year, month, on_date_selected, selected_day=selected_day),
                box="EMPTY"
            )
            month_widgets.append(container)

        # Fill with empty if less than 3
        while len(month_widgets) < 3:
            month_widgets.append(ptg.Label(""))

        widgets = [
            NavigationWidget(active_page="calendar"),
        ]
        widgets.extend(month_widgets)

        title_range = f"{month_names[0]} - {month_names[-1]}"
        return widgets, f"[green]Calendar - {title_range} {year}[/]"

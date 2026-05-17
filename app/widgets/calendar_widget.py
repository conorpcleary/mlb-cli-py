"""
Calendar widget for the MLB CLI application.
"""
import calendar
import pytermgui as ptg
from .separator import Separator


class CalendarButton(ptg.Button):
    """
    A button that only responds to keyboard events.
    """

    def handle_mouse(self, event):
        """Ignores mouse events."""
        return False


class CalendarWidget(ptg.Container):
    """
    A widget that displays a calendar for a specific month.
    Allows selecting a date and confirming with ENTER.
    """

    def __init__(self, year, month, on_date_selected, selected_day=None, **kwargs):
        """
        Initializes the CalendarWidget.

        Args:
            year (int): The year to display.
            month (int): The month to display.
            on_date_selected (callable): Callback when a date is selected with ENTER.
            selected_day (int, optional): The day to highlight as selected.
            **kwargs: Additional arguments for ptg.Container.
        """
        super().__init__(**kwargs)
        self.year = year
        self.month = month
        self.on_date_selected = on_date_selected
        self.day_to_button = {}
        self.button_to_day = {}
        self.border = ptg.boxes.SINGLE

        cal = calendar.Calendar(firstweekday=6)  # Sunday
        month_days = cal.monthdayscalendar(year, month)

        widgets = []
        # Header: Su Mo Tu We Th Fr Sa
        days_header = ptg.Splitter(
            *[ptg.Label(d, parent_align=ptg.HorizontalAlignment.CENTER)
              for d in ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]]
        )
        widgets.append(days_header)
        widgets.append(Separator())

        for week in month_days:
            week_widgets = []
            for day in week:
                if day == 0:
                    week_widgets.append(ptg.Label(""))
                else:
                    btn = CalendarButton(
                        str(day),
                        lambda b, d=day: self.on_date_selected(self.year, self.month, d)
                    )
                    if day == selected_day:
                        btn.styles.label = "inverse"
                    else:
                        btn.styles.label = "white"

                    btn.styles.highlight = "inverse"

                    self.day_to_button[day] = btn
                    self.button_to_day[btn] = day
                    week_widgets.append(btn)
            widgets.append(ptg.Splitter(*week_widgets))

        self.set_widgets(widgets)

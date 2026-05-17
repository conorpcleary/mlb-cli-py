"""
Navigation widget for the MLB CLI application.
"""
import pytermgui as ptg


class NavigationWidget(ptg.Container):
    """
    A persistent navigation bar widget shown at the top of every screen.
    Displays available pages and their hotkeys, highlighting the active one.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, active_page=None, **kwargs):
        """
        Initializes the NavigationWidget.

        Args:
            active_page (str, optional): The name of the currently active screen.
            **kwargs: Additional arguments for ptg.Container.
        """
        super().__init__(**kwargs)
        self.border = ptg.boxes.EMPTY

        if active_page == "standings":
            self.schedule_label = ptg.Label(
                "Back to Schedule [bold][cyan]x[/]",
                parent_align=ptg.HorizontalAlignment.CENTER)
            self.calendar_label = ptg.Label(
                "Back to Calendar [bold][cyan]c[/]",
                parent_align=ptg.HorizontalAlignment.CENTER)
            self.set_widgets([ptg.Splitter(self.schedule_label, self.calendar_label)])
            return

        if active_page == "calendar":
            self.prev_label = ptg.Label(
                "Prev Page [bold][cyan][[/]",
                parent_align=ptg.HorizontalAlignment.CENTER)
            self.next_label = ptg.Label(
                "Next Page [bold][cyan]][/]",
                parent_align=ptg.HorizontalAlignment.CENTER)
            self.stand_label = ptg.Label(
                "Standings [bold][cyan]x[/]",
                parent_align=ptg.HorizontalAlignment.CENTER)
            self.set_widgets([ptg.Splitter(self.prev_label, self.next_label, self.stand_label)])
            return

        # Default: Schedule page navigation
        self.prev_label = ptg.Label(
            "Prev [bold][cyan][[/]",
            parent_align=ptg.HorizontalAlignment.CENTER)
        self.next_label = ptg.Label(
            "Next [bold][cyan]][/]",
            parent_align=ptg.HorizontalAlignment.CENTER)
        self.today_label = ptg.Label(
            "Today [bold][cyan]t[/]",
            parent_align=ptg.HorizontalAlignment.CENTER)
        self.cal_label = ptg.Label(
            "Calendar [bold][cyan]c[/]",
            parent_align=ptg.HorizontalAlignment.CENTER)
        self.stand_label = ptg.Label(
            "Standings [bold][cyan]x[/]",
            parent_align=ptg.HorizontalAlignment.CENTER)

        self.splitter = ptg.Splitter(
            self.prev_label,
            self.next_label,
            self.today_label,
            self.cal_label,
            self.stand_label,
        )

        self.set_widgets([self.splitter])

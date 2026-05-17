"""
Separator widget for the MLB CLI application.
"""
import pytermgui as ptg


class Separator(ptg.Label):
    """A simple horizontal line separator widget."""

    def __init__(self, **kwargs):
        super().__init__("─" * 10, **kwargs)

"""
Base module for data source abstractions.
Provides the interface for fetching MLB data.
"""
from abc import ABC, abstractmethod


class BaseDataSource(ABC):
    """
    Abstract base class for all MLB data sources.
    Defines the contract for fetching team info, schedules, and standings.
    """

    @abstractmethod
    def fetch_teams(self):
        """Fetches all MLB teams and returns a mapping of ID to abbreviation."""

    @abstractmethod
    def fetch_schedule(self, date_str):
        """Fetches the MLB schedule for a specific date."""

    @abstractmethod
    def fetch_standings(self):
        """Fetches current MLB standings."""

    @abstractmethod
    def fetch_wild_card(self, league_id):
        """Fetches wild card standings for a league."""

    @abstractmethod
    def fetch_boxscore(self, game_id):
        """Fetches boxscore data for a specific game."""

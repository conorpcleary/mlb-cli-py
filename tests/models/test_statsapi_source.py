"""
Unit tests for StatsApiDataSource.
"""
import unittest
from unittest.mock import patch
from app.models.statsapi_source import StatsApiDataSource
from app.exceptions import APIError


class TestStatsApiDataSource(unittest.TestCase):
    """Test cases for StatsApiDataSource."""

    def setUp(self):
        self.source = StatsApiDataSource()

    @patch('statsapi.get')
    def test_fetch_teams_success(self, mock_get):
        """Test fetch_teams with success."""
        mock_get.return_value = {'teams': [{'id': 1, 'abbreviation': 'NYY', 'name': 'Yankees'}]}
        teams = self.source.fetch_teams()
        self.assertEqual(teams[1], 'NYY')

    @patch('statsapi.get')
    def test_fetch_teams_fallback(self, mock_get):
        """Test fetch_teams with failure triggers fallback."""
        mock_get.side_effect = RuntimeError("API Down")
        teams = self.source.fetch_teams()
        self.assertIn(147, teams)

    @patch('statsapi.schedule')
    def test_fetch_schedule_success(self, mock_schedule):
        """Test fetch_schedule with success."""
        mock_schedule.return_value = [{'id': 1}]
        res = self.source.fetch_schedule('01/01/2026')
        self.assertEqual(res[0]['id'], 1)

    @patch('statsapi.schedule')
    def test_fetch_schedule_failure(self, mock_schedule):
        """Test fetch_schedule with failure."""
        mock_schedule.side_effect = RuntimeError("Error")
        with self.assertRaises(APIError):
            self.source.fetch_schedule('01/01/2026')

    @patch('statsapi.get')
    def test_fetch_standings_success(self, mock_get):
        """Test fetch_standings with success."""
        mock_get.return_value = {'records': [{'division': {'id': 201}, 'teamRecords': []}]}
        res = self.source.fetch_standings()
        self.assertEqual(len(res), 1)

    @patch('statsapi.get')
    def test_fetch_standings_failure(self, mock_get):
        """Test fetch_standings with failure."""
        mock_get.side_effect = RuntimeError("Error")
        with self.assertRaises(APIError):
            self.source.fetch_standings()

    @patch('statsapi.get')
    def test_fetch_wild_card_success(self, mock_get):
        """Test fetch_wild_card with success."""
        mock_get.return_value = {'records': [{'teamRecords': []}]}
        res = self.source.fetch_wild_card(103)
        self.assertIsNotNone(res)

    @patch('statsapi.get')
    def test_fetch_wild_card_failure(self, mock_get):
        """Test fetch_wild_card with failure."""
        mock_get.side_effect = RuntimeError("Error")
        with self.assertRaises(APIError):
            self.source.fetch_wild_card(103)

    @patch('statsapi.boxscore_data')
    def test_fetch_boxscore_success(self, mock_box):
        """Test fetch_boxscore with success."""
        mock_box.return_value = {'id': 123}
        res = self.source.fetch_boxscore(123)
        self.assertEqual(res['id'], 123)

    @patch('statsapi.boxscore_data')
    def test_fetch_boxscore_failure(self, mock_box):
        """Test fetch_boxscore with failure."""
        mock_box.side_effect = RuntimeError("Error")
        with self.assertRaises(APIError):
            self.source.fetch_boxscore(123)

"""
Unit tests for the data_service module.
"""
import unittest
from unittest.mock import patch
from datetime import datetime
from app.models.data_service import (
    fetch_teams,
    get_team_abbr,
    fetch_schedule,
    get_yesterday_date,
    get_today_date,
    fetch_wild_card,
    fetch_standings,
    TEAMS
)

class TestDataService(unittest.TestCase):
    """Test cases for data_service.py functions."""

    def setUp(self):
        """Reset TEAMS cache before each test."""
        TEAMS.clear()

    @patch('statsapi.get')
    def test_fetch_teams_success(self, mock_get):
        """Test successful team fetching and caching."""
        mock_get.return_value = {
            'teams': [
                {'id': 1, 'abbreviation': 'NYY', 'name': 'New York Yankees'},
                {'id': 2, 'name': 'Boston Red Sox'} # No abbreviation, should use name
            ]
        }
        fetch_teams()
        self.assertEqual(TEAMS[1], 'NYY')
        self.assertEqual(TEAMS[2], 'BOS')

    @patch('statsapi.get')
    def test_fetch_teams_failure(self, mock_get):
        """Test fallback behavior when API fails."""
        mock_get.side_effect = RuntimeError("API Down")
        fetch_teams()
        self.assertEqual(TEAMS[147], 'NYY')
        self.assertEqual(TEAMS[110], 'BAL')

    @patch('app.models.data_service.fetch_teams')
    def test_get_team_abbr_calls_fetch_if_empty(self, mock_fetch):
        """Test that get_team_abbr triggers fetch_teams if cache is empty."""
        def side_effect():
            TEAMS[1] = 'TEST'
        mock_fetch.side_effect = side_effect

        abbr = get_team_abbr(1)
        mock_fetch.assert_called_once()
        self.assertEqual(abbr, 'TEST')

    def test_get_team_abbr_cached(self):
        """Test get_team_abbr returns cached value."""
        TEAMS[1] = 'TEST'
        self.assertEqual(get_team_abbr(1), 'TEST')

    def test_get_team_abbr_not_found(self):
        """Test get_team_abbr returns string ID if not in cache."""
        TEAMS[1] = 'TEST'
        self.assertEqual(get_team_abbr(999), '999')

    @patch('statsapi.schedule')
    def test_fetch_schedule(self, mock_schedule):
        """Test fetch_schedule calls statsapi.schedule."""
        mock_schedule.return_value = [{'game_id': 123}]
        result = fetch_schedule('01/01/2024')
        mock_schedule.assert_called_with(date='01/01/2024')
        self.assertEqual(result, [{'game_id': 123}])

    @patch('app.models.data_service.datetime')
    def test_get_today_date(self, mock_datetime):
        """Test today's date formatting."""
        mock_datetime.now.return_value = datetime(2024, 1, 1)
        self.assertEqual(get_today_date(), '01/01/2024')

    @patch('app.models.data_service.datetime')
    def test_get_yesterday_date(self, mock_datetime):
        """Test yesterday's date formatting."""
        mock_datetime.now.return_value = datetime(2024, 1, 2)
        self.assertEqual(get_yesterday_date(), '01/01/2024')

    @patch('statsapi.get')
    def test_fetch_wild_card_success(self, mock_get):
        """Test successful wild card fetching."""
        mock_get.return_value = {
            'records': [{
                'teamRecords': [
                    {
                        'team': {'id': 1},
                        'wins': 90,
                        'losses': 72,
                        'wildCardGamesBack': '-'
                    }
                ]
            }]
        }
        result = fetch_wild_card(103)
        self.assertEqual(result['div_name'], 'AL Wild Card')
        self.assertEqual(len(result['teams']), 1)
        self.assertEqual(result['teams'][0]['w'], 90)

    @patch('statsapi.get')
    def test_fetch_wild_card_failure(self, mock_get):
        """Test fetch_wild_card handling API failure."""
        mock_get.side_effect = RuntimeError("API Down")
        result = fetch_wild_card(103)
        self.assertIsNone(result)

    @patch('statsapi.get')
    def test_fetch_wild_card_truncation(self, mock_get):
        """Test that wild card teams are truncated to 7."""
        mock_get.return_value = {
            'records': [{
                'teamRecords': [{'team': {'id': i}, 'wins': 0, 'losses': 0} for i in range(10)]
            }]
        }
        result = fetch_wild_card(103)
        self.assertEqual(len(result['teams']), 7)

    @patch('statsapi.get')
    def test_fetch_wild_card_no_records(self, mock_get):
        """Test fetch_wild_card when API returns no records."""
        mock_get.return_value = {'records': []}
        result = fetch_wild_card(103)
        self.assertIsNone(result)

    @patch('app.models.data_service.fetch_wild_card')
    @patch('statsapi.standings_data')
    def test_fetch_standings(self, mock_standings, mock_wc):
        """Test fetch_standings maps division IDs and includes wild card."""
        mock_data = {
            201: {'div_name': 'ALE'}, 202: {'div_name': 'ALC'}, 200: {'div_name': 'ALW'},
            204: {'div_name': 'NLE'}, 205: {'div_name': 'NLC'}, 203: {'div_name': 'NLW'}
        }
        mock_standings.return_value = mock_data
        mock_wc.side_effect = lambda lid: {'div_name': f"{lid} WC"}

        al, nl, al_wc, nl_wc = fetch_standings()

        self.assertEqual(len(al), 3)
        self.assertEqual(len(nl), 3)
        self.assertEqual(al_wc['div_name'], '103 WC')
        self.assertEqual(nl_wc['div_name'], '104 WC')

if __name__ == '__main__':
    unittest.main()

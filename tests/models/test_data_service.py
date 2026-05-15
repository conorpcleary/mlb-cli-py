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
    # pylint: disable=too-many-public-methods

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
        # Mock cache miss
        with patch('app.models.data_service.get_cached_data', return_value=None), \
             patch('app.models.data_service.set_cached_data'):
            result = fetch_schedule('01/01/2024')
            mock_schedule.assert_called_with(date='01/01/2024')
            self.assertEqual(result, [{'game_id': 123}])

    @patch('app.models.data_service.get_cached_data')
    def test_fetch_schedule_cache_hit(self, mock_cache):
        """Test fetch_schedule returns cached data."""
        mock_cache.return_value = [{'game_id': 999}]
        result = fetch_schedule('01/01/2024')
        self.assertEqual(result, [{'game_id': 999}])

    @patch('app.models.data_service.set_cached_data')
    @patch('app.models.data_service.get_cached_data')
    @patch('statsapi.schedule')
    def test_fetch_schedule_cache_miss_today(self, mock_schedule, mock_get_cache, mock_set_cache):
        """Test fetch_schedule sets TTL for today's schedule."""
        mock_get_cache.return_value = None
        mock_schedule.return_value = [{'id': 1}]

        with patch('app.models.data_service.get_today_date', return_value='01/01/2024'):
            fetch_schedule('01/01/2024')
            mock_set_cache.assert_called_with(
                'schedule:01/01/2024', [{'id': 1}], ttl=300
            )

    @patch('app.models.data_service.set_cached_data')
    @patch('app.models.data_service.get_cached_data')
    @patch('statsapi.schedule')
    def test_fetch_schedule_cache_miss_yesterday(self, mock_sched, mock_get_c, mock_set_c):
        """Test fetch_schedule uses no TTL for other dates (yesterday)."""
        mock_get_c.return_value = None
        mock_sched.return_value = [{'id': 1}]

        with patch('app.models.data_service.get_today_date', return_value='01/02/2024'):
            fetch_schedule('01/01/2024')
            mock_set_c.assert_called_with('schedule:01/01/2024', [{'id': 1}], ttl=None)

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

    @patch('app.models.data_service.get_cached_data')
    @patch('statsapi.get')
    def test_fetch_wild_card_cache_hit(self, _mock_get, mock_cache):
        """Test fetch_wild_card returns cached data."""
        mock_cache.return_value = {'div_name': 'Cached WC'}
        result = fetch_wild_card(103)
        self.assertEqual(result['div_name'], 'Cached WC')

    @patch('app.models.data_service.get_cached_data')
    @patch('statsapi.get')
    def test_fetch_standings_cache_hit(self, _mock_get, mock_cache):
        """Test fetch_standings returns cached data as tuple."""
        mock_cache.return_value = [[], [], {}, {}]
        result = fetch_standings()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 4)

    @patch('app.models.data_service.get_cached_data', return_value=None)
    @patch('app.models.data_service.set_cached_data')
    @patch('statsapi.get')
    def test_fetch_wild_card_success(self, mock_get, _mock_set, _mock_get_c):
        """Test successful wild card fetching with pct and l10."""
        mock_get.return_value = {
            'records': [{
                'teamRecords': [
                    {
                        'team': {'id': 1},
                        'wins': 90,
                        'losses': 72,
                        'wildCardGamesBack': '-',
                        'winningPercentage': '.556',
                        'records': {
                            'splitRecords': [
                                {'type': 'lastTen', 'wins': 6, 'losses': 4}
                            ]
                        }
                    }
                ]
            }]
        }
        result = fetch_wild_card(103)
        self.assertEqual(result['div_name'], 'AL Wild Card')
        self.assertEqual(len(result['teams']), 1)
        self.assertEqual(result['teams'][0]['w'], 90)
        self.assertEqual(result['teams'][0]['pct'], '55.6%')
        self.assertEqual(result['teams'][0]['l10'], '6-4')

    @patch('statsapi.get')
    def test_fetch_wild_card_failure(self, mock_get):
        """Test fetch_wild_card handling API failure."""
        mock_get.side_effect = RuntimeError("API Down")
        # Mock cache miss
        with patch('app.models.data_service.get_cached_data', return_value=None):
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
        with patch('app.models.data_service.get_cached_data', return_value=None), \
             patch('app.models.data_service.set_cached_data'):
            result = fetch_wild_card(103)
            self.assertEqual(len(result['teams']), 7)

    @patch('statsapi.get')
    def test_fetch_wild_card_no_records(self, mock_get):
        """Test fetch_wild_card when API returns no records."""
        mock_get.return_value = {'records': []}
        with patch('app.models.data_service.get_cached_data', return_value=None):
            result = fetch_wild_card(103)
            self.assertIsNone(result)

    @patch('statsapi.get')
    def test_parse_team_record_invalid_pct(self, mock_get):
        """Test _parse_team_record with invalid winningPercentage."""
        mock_get.return_value = {
            'records': [{
                'teamRecords': [{
                    'team': {'id': 1},
                    'wins': 90,
                    'losses': 72,
                    'winningPercentage': 'invalid'
                }]
            }]
        }
        with patch('app.models.data_service.get_cached_data', return_value=None), \
             patch('app.models.data_service.set_cached_data'):
            result = fetch_wild_card(103)
            self.assertEqual(result['teams'][0]['pct'], '-')

    @patch('app.models.data_service.fetch_wild_card')
    @patch('statsapi.get')
    def test_fetch_standings_no_data(self, mock_get, _mock_wc):
        """Test fetch_standings when API returns no data."""
        mock_get.return_value = None
        with patch('app.models.data_service.get_cached_data', return_value=None):
            al, nl, _, _ = fetch_standings()
            self.assertEqual(al, [])
            self.assertEqual(nl, [])

    @patch('app.models.data_service.fetch_wild_card')
    @patch('statsapi.get')
    def test_fetch_standings_failure(self, mock_get, _mock_wc):
        """Test fetch_standings handling API failure."""
        mock_get.side_effect = RuntimeError("API Down")
        with patch('app.models.data_service.get_cached_data', return_value=None):
            al, nl, _, _ = fetch_standings()
            self.assertEqual(al, [])
            self.assertEqual(nl, [])

    @patch('app.models.data_service.fetch_wild_card')
    @patch('app.models.data_service.get_cached_data', return_value=None)
    @patch('app.models.data_service.set_cached_data')
    @patch('statsapi.get')
    def test_fetch_standings(self, mock_get, _mock_set, _mock_get_c, mock_wc):
        """Test fetch_standings maps division IDs and includes wild card."""
        mock_get.return_value = {
            'records': [
                {
                    'division': {'id': 201, 'name': 'AL East'},
                    'teamRecords': [{'team': {'id': 1}, 'wins': 90, 'losses': 72}]
                },
                {
                    'division': {'id': 204, 'name': 'NL East'},
                    'teamRecords': [{'team': {'id': 2}, 'wins': 85, 'losses': 77}]
                }
            ]
        }
        mock_wc.side_effect = lambda lid: {'div_name': f"{lid} WC"}

        al, nl, al_wc, nl_wc = fetch_standings()

        self.assertEqual(al[0]['div_name'], 'AL East')
        self.assertIsNone(al[1])
        self.assertEqual(nl[0]['div_name'], 'NL East')
        self.assertEqual(al_wc['div_name'], '103 WC')
        self.assertEqual(nl_wc['div_name'], '104 WC')

if __name__ == '__main__':  # pragma: no cover
    unittest.main()

"""
Implementation of BaseDataSource using the statsapi library.
"""
import statsapi
from app.config import DIVISION_NAMES
from app.logger import get_logger
from app.exceptions import APIError
from .base_data_source import BaseDataSource

logger = get_logger(__name__)


class StatsApiDataSource(BaseDataSource):
    """
    Data source implementation that fetches data from the MLB StatsAPI.
    """

    def fetch_teams(self):
        """Fetches all MLB teams and returns a mapping of ID to abbreviation."""
        try:
            teams_data = statsapi.get('teams', {'sportId': 1})['teams']
            return {t['id']: t.get('abbreviation', t['name'][:3].upper()) for t in teams_data}
        except (ValueError, KeyError, IndexError, RuntimeError, TypeError, AttributeError) as e:
            logger.error("Failed to fetch teams: %s", e)
            # Fallback to some common ones if API fails
            return {147: 'NYY', 110: 'BAL', 119: 'LAD'}

    def fetch_schedule(self, date_str):
        """Fetches the MLB schedule for a specific date."""
        try:
            return statsapi.schedule(date=date_str)
        except (ValueError, KeyError, IndexError, RuntimeError, TypeError, AttributeError) as e:
            logger.error("Failed to fetch schedule for %s: %s", date_str, e)
            raise APIError(f"Unable to fetch schedule for {date_str}") from e

    def fetch_standings(self):
        """Fetches current MLB standings."""
        try:
            data = statsapi.get('standings', {'leagueId': '103,104'})
            if not data or not data.get('records'):
                return []

            div_results = []
            for record in data['records']:
                div_id = record.get('division', {}).get('id')
                if div_id:
                    div_results.append({
                        'id': div_id,
                        'name': DIVISION_NAMES.get(
                            div_id, record.get('division', {}).get('name', 'Unknown')
                        ),
                        'teams': record.get('teamRecords', [])
                    })
            return div_results
        except (ValueError, KeyError, IndexError, RuntimeError, TypeError, AttributeError) as e:
            logger.error("Failed to fetch standings: %s", e)
            raise APIError("Unable to fetch standings") from e

    def fetch_wild_card(self, league_id):
        """Fetches wild card standings for a league."""
        try:
            data = statsapi.get('standings', {
                'leagueId': league_id,
                'standingsTypes': 'wildCard'
            })
            if not data or not data.get('records'):
                return None
            return data['records'][0]
        except (ValueError, KeyError, IndexError, RuntimeError, TypeError, AttributeError) as e:
            logger.error("Failed to fetch wild card for league %s: %s", league_id, e)
            raise APIError(f"Unable to fetch wild card standings for league {league_id}") from e

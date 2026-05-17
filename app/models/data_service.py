"""
Data service module for fetching MLB data.
Delegates to a BaseDataSource implementation (defaulting to StatsApiDataSource).
"""
from datetime import datetime, timedelta
from app.config import LIVE_DATA_TTL
from app.models.cache_service import get_cached_data, set_cached_data
from .statsapi_source import StatsApiDataSource

# Global cache for team abbreviations
TEAMS = {}

# Default data source
_data_source = StatsApiDataSource()


def fetch_teams():
    """
    Fetches all MLB teams and populates the global TEAMS cache with abbreviations.
    """
    TEAMS.clear()
    TEAMS.update(_data_source.fetch_teams())


def get_team_abbr(team_id):
    """
    Retrieves the abbreviation for a given team ID.
    Populates the TEAMS cache if it is empty.
    """
    if not TEAMS:
        fetch_teams()
    return TEAMS.get(team_id, str(team_id))


def fetch_schedule(date_str):
    """
    Fetches the MLB schedule for a specific date.

    Args:
        date_str (str): The date string in MM/DD/YYYY format.

    Returns:
        list: A list of game dictionaries.
    """
    cache_key = f"schedule:{date_str}"
    cached = get_cached_data(cache_key)
    if cached is not None:
        return cached

    data = _data_source.fetch_schedule(date_str)

    # Policy: Today has TTL, other dates don't
    ttl = LIVE_DATA_TTL if date_str == get_today_date() else None
    set_cached_data(cache_key, data, ttl=ttl)

    return data


def format_date(dt):
    """Formats a datetime object to MM/DD/YYYY."""
    return dt.strftime('%m/%d/%Y')


def parse_date(date_str):
    """Parses a MM/DD/YYYY string into a datetime object."""
    return datetime.strptime(date_str, '%m/%d/%Y')


def get_yesterday_date():
    """
    Returns yesterday's date as a formatted string.

    Returns:
        str: Date in MM/DD/YYYY format.
    """
    return (datetime.now() - timedelta(days=1)).strftime('%m/%d/%Y')


def get_today_date():
    """
    Returns today's date as a formatted string.

    Returns:
        str: Date in MM/DD/YYYY format.
    """
    return datetime.now().strftime('%m/%d/%Y')


def _parse_team_record(tr, is_wild_card=False):
    """Parses a team record from the API into a simplified dictionary."""
    # Find last 10 record
    l10 = "-"
    if 'records' in tr and 'splitRecords' in tr['records']:
        for split in tr['records']['splitRecords']:
            if split['type'] == 'lastTen':
                l10 = f"{split['wins']}-{split['losses']}"
                break

    # Format winning percentage (e.g., .500 -> 50.0%)
    pct_val = tr.get('winningPercentage', '0')
    try:
        pct_float = float(pct_val) * 100
        pct_str = f"{pct_float:.1f}%"
    except (ValueError, TypeError):
        pct_str = "-"

    # Prioritize wildCardGamesBack for wild card view, else use gamesBack
    if is_wild_card:
        gb = tr.get('wildCardGamesBack', tr.get('gamesBack', '-'))
    else:
        gb = tr.get('gamesBack', '-')

    return {
        'team_id': tr['team']['id'],
        'w': tr['wins'],
        'l': tr['losses'],
        'gb': gb,
        'pct': pct_str,
        'l10': l10
    }


def fetch_wild_card(league_id):
    """
    Fetches the wild card standings for a specific league.

    Args:
        league_id (int): The ID of the league (103 for AL, 104 for NL).

    Returns:
        dict: Wild card standings data.
    """
    cache_key = f"wildcard:{league_id}"
    cached = get_cached_data(cache_key)
    if cached is not None:
        return cached

    record = _data_source.fetch_wild_card(league_id)
    if not record:
        return None

    teams = [_parse_team_record(tr, is_wild_card=True) for tr in record.get('teamRecords', [])]

    league_name = "AL" if league_id == 103 else "NL"
    result = {
        'div_name': f"{league_name} Wild Card",
        'teams': teams[:7]
    }
    set_cached_data(cache_key, result, ttl=LIVE_DATA_TTL)
    return result


def fetch_standings():
    """
    Fetches the current MLB standings for the American and National Leagues,
    including divisions and wild card.

    Returns:
        tuple: (al_divs, nl_divs, al_wc, nl_wc)
    """
    cache_key = "standings:full"
    cached = get_cached_data(cache_key)
    if cached is not None:
        return tuple(cached)

    div_results = _data_source.fetch_standings()
    if not div_results:
        return [], [], None, None

    div_map = {}
    for div in div_results:
        div_map[div['id']] = {
            'div_name': div['name'],
            'teams': [
                _parse_team_record(tr, is_wild_card=False)
                for tr in div['teams']
            ]
        }

    # AL IDs: East(201), Central(202), West(200)
    # NL IDs: East(204), Central(205), West(203)
    al_divs = [div_map.get(201), div_map.get(202), div_map.get(200)]
    nl_divs = [div_map.get(204), div_map.get(205), div_map.get(203)]

    al_wc = fetch_wild_card(103)
    nl_wc = fetch_wild_card(104)

    result = (al_divs, nl_divs, al_wc, nl_wc)
    set_cached_data(cache_key, result, ttl=LIVE_DATA_TTL)
    return result

"""
Data service module for fetching MLB data via the statsapi library.
Provides functions for team abbreviations, schedules, and standings.
"""
from datetime import datetime, timedelta
import statsapi

# Global cache for team abbreviations
TEAMS = {}


def fetch_teams():
    """
    Fetches all MLB teams and populates the global TEAMS cache with abbreviations.
    Defaults to specific common teams if the API request fails.
    """
    try:
        teams_data = statsapi.get('teams', {'sportId': 1})['teams']
        for t in teams_data:
            TEAMS[t['id']] = t.get('abbreviation', t['name'][:3].upper())
    except (ValueError, KeyError, IndexError, RuntimeError, TypeError, AttributeError):
        # Fallback to some common ones if API fails
        TEAMS.update({147: 'NYY', 110: 'BAL', 119: 'LAD'})


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
    return statsapi.schedule(date=date_str)


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


def fetch_wild_card(league_id):
    """
    Fetches the wild card standings for a specific league.

    Args:
        league_id (int): The ID of the league (103 for AL, 104 for NL).

    Returns:
        dict: Wild card standings data.
    """
    try:
        data = statsapi.get('standings', {
            'leagueId': league_id,
            'standingsTypes': 'wildCard'
        })
        if not data or not data.get('records'):
            return None

        record = data['records'][0]
        teams = []
        for tr in record.get('teamRecords', []):
            teams.append({
                'team_id': tr['team']['id'],
                'w': tr['wins'],
                'l': tr['losses'],
                'gb': tr.get('wildCardGamesBack', '-')
            })

        league_name = "AL" if league_id == 103 else "NL"
        return {
            'div_name': f"{league_name} Wild Card",
            'teams': teams[:7]
        }
    except (ValueError, KeyError, IndexError, RuntimeError, TypeError, AttributeError):
        return None


def fetch_standings():
    """
    Fetches the current MLB standings for the American and National Leagues,
    including divisions and wild card.

    Returns:
        tuple: (al_divs, nl_divs, al_wc, nl_wc)
    """
    # AL IDs: East(201), Central(202), West(200)
    # NL IDs: East(204), Central(205), West(203)
    data = statsapi.standings_data(leagueId='103,104')

    al_divs = [data.get(201), data.get(202), data.get(200)]
    nl_divs = [data.get(204), data.get(205), data.get(203)]

    al_wc = fetch_wild_card(103)
    nl_wc = fetch_wild_card(104)

    return al_divs, nl_divs, al_wc, nl_wc

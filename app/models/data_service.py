import statsapi
from datetime import datetime, timedelta

TEAMS = {}


def fetch_teams():
    global TEAMS
    try:
        teams_data = statsapi.get('teams', {'sportId': 1})['teams']
        for t in teams_data:
            TEAMS[t['id']] = t.get('abbreviation', t['name'][:3].upper())
    except Exception:
        # Fallback to some common ones if API fails
        TEAMS.update({147: 'NYY', 110: 'BAL', 119: 'LAD'})


def get_team_abbr(team_id):
    if not TEAMS:
        fetch_teams()
    return TEAMS.get(team_id, str(team_id))


def fetch_schedule(date_str):
    """Fetches games for a specific date string (MM/DD/YYYY)."""
    return statsapi.schedule(date=date_str)


def get_yesterday_date():
    return (datetime.now() - timedelta(days=1)).strftime('%m/%d/%Y')


def get_today_date():
    return datetime.now().strftime('%m/%d/%Y')


def fetch_standings():
    """Fetches standings for AL (103) and NL (104)."""
    # AL IDs: East(201), Central(202), West(200)
    # NL IDs: East(204), Central(205), West(203)
    data = statsapi.standings_data(leagueId='103,104')

    al_divs = [data.get(201), data.get(202), data.get(200)]
    nl_divs = [data.get(204), data.get(205), data.get(203)]

    return al_divs, nl_divs

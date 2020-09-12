from datetime import datetime
import json
from urllib.request import Request, urlopen

from params import HEADERS


class Team:
    """Data class for team data
    """
    def __init__(self, team_data):
        self.name = team_data['team_name']
        self.id = team_data['team_id']

        
class Fixture:
    BADGE_LOOKUPS = {
        42: ':afc:',      # Arsenal
        63: ':leeds:',    # Leeds
        1373: ':lofc:',   # Leyton Orient
        50: ':mcfc:',     # Manchester City
        34: ':nufc:',     # Newcastle
        1351: ':pvfc:',   # Port Vale
        41: ':sfc:',      # Southampton
    }
    def __init__(self, data_dict):
        self.datetime = datetime.fromtimestamp(data_dict['event_timestamp'])
        self.home_team = Team(data_dict['homeTeam'])
        self.away_team = Team(data_dict['awayTeam'])
        self.competition = data_dict['league']['name']
        self.status = data_dict['statusShort']
        
    @property
    def is_today(self):
        """Checks whether a fixture is taking place on the current day.

        Returns:
            bool: True if the match is taking place on the current day and not 
                  postponed, cancelled, abandoned etc, else False
        """
        return (
            self.datetime.date() == datetime.now().date()
            and self.status not in ('PST', 'CANC', 'ABD', 'AWD', 'WO')
        )
    
    @property
    def description(self):
        """Gives description text for the fixture with emoji codes for given teams 

        Returns:
            str: match description string including teams, time and competition.
        """
        home_msg = Fixture.BADGE_LOOKUPS.get(
            self.home_team.id, self.home_team.name
        )
        away_msg = Fixture.BADGE_LOOKUPS.get(
            self.away_team.id, self.away_team.name
        )
        start_time = self.datetime.strftime('%H:%M')
        return f'{home_msg} vs {away_msg} @ {start_time} ({self.competition})'


def get_active_fixtures():
    current_matches = []

    for team in Fixture.BADGE_LOOKUPS.keys():
        next_fix_url = f'https://api-football-v1.p.rapidapi.com/v2/fixtures/team/{team}/next/1'

        fix_req = Request(next_fix_url, headers=HEADERS)
        
        fix_content = urlopen(fix_req).read()
        
        data = json.loads(fix_content)
        fix = Fixture(data['api']['fixtures'][0])
        if fix.is_today and not fix.description in current_matches:
            current_matches.append(fix.description)

    return current_matches
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
        
    def form(self, matches=5):
        form_url = (
            f'https://api-football-v1.p.rapidapi.com/v2/fixtures/team/'
            f'{self.id}/last/{matches}'
        )

        # Load up the fixtures
        form_req = Request(form_url, headers=HEADERS)
        form_content = urlopen(form_req).read()
        data = json.loads(form_content)
        
        return ''.join(Fixture(f).result(self) for f in data['api']['fixtures'])
        
    def __eq__(self, other):
        return self.id == other.id
        

class Fixture:
    BADGE_LOOKUPS = {
        42: '<:afc:735119993175277578>',      # Arsenal
        63: '<:leeds:735122574920384542>',    # Leeds
        1373: '<:lofc:735119992978407525>',   # Leyton Orient
        50: '<:mcfc:735119993645039676>',     # Manchester City
        34: '<:nufc:753175503992651826>',     # Newcastle
        1351: '<:pvfc:735119353367887922>',   # Port Vale
        41: '<:sfc:735119993510953051>',      # Southampton
        75: '<:scfc:761638560281264149>',     # The neighbours
    }
    def __init__(self, data_dict):
        self._data = data_dict
        self.datetime = datetime.fromtimestamp(data_dict['event_timestamp'])
        self.home_team = Team(data_dict['homeTeam'])
        self.away_team = Team(data_dict['awayTeam'])
        self.competition = data_dict['league']['name']
        self.status = data_dict['statusShort']
    
    @property
    def inactive(self):
        return self.status in ('PST', 'CANC', 'ABD', 'AWD', 'WO')

    @property
    def is_today(self):
        """Checks whether a fixture is taking place on the current day.

        Returns:
            bool: True if the match is taking place on the current day and not 
                  postponed, cancelled, abandoned etc, else False
        """
        return (
            self.datetime.date() == datetime.now().date()
            and not self.inactive
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
        
        home_form = self.home_team.form()
        away_msg = Fixture.BADGE_LOOKUPS.get(
            self.away_team.id, self.away_team.name
        )
        away_form = self.away_team.form()
        start_time = self.datetime.strftime('%H:%M')
        return (
            f'{home_msg} ({home_form}) vs {away_msg} ({away_form}) '
            f'@ {start_time} ({self.competition})'
        )
    
    def result(self, team: Team):
        if self.home_team == team:
            us, them = 'Home', 'Away'
        elif self.away_team == team:
            us, them = 'Away', 'Home'
        else:
            raise ValueError('Team not involved')
        
        if self.inactive:
            return ':black_circle:'

        if self._data[f'goals{us}Team'] > self._data[f'goals{them}Team']:
            return ':blue_circle:'
        elif self._data[f'goals{us}Team'] < self._data[f'goals{them}Team']:
            return ':red_circle:'
        else:
            return ':yellow_circle:'


def get_active_fixtures():
    current_matches = []
    seen_teams = []

    for team in Fixture.BADGE_LOOKUPS.keys():
        if team in seen_teams:
            continue
        next_fix_url = f'https://api-football-v1.p.rapidapi.com/v2/fixtures/team/{team}/next/1'

        fix_req = Request(next_fix_url, headers=HEADERS)
        
        fix_content = urlopen(fix_req).read()
        
        data = json.loads(fix_content)
        fix = Fixture(data['api']['fixtures'][0])
        if fix.is_today:
            current_matches.append(fix.description)
        
        seen_teams.extend([fix.home_team.id, fix.away_team.id])

    return current_matches
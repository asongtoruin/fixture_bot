from discord.ext.commands import Bot

from .fixtures import get_next_team_fixture, get_competition_fixtures


class FixtureBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tracked_teams = set()
        self.tracked_competitions = set()

        self.active_fixtures = []

    def track_teams(self, *teams):
        self.tracked_teams.update(teams)
    
    def track_competitions(self, *competitions):
        self.tracked_competitions.update(competitions)
    
    def get_fixtures(self, today_only=True, date=None):
        if today_only:
            date = 'today'

        for team in self.tracked_teams:
            fix = get_next_team_fixture(team, today_only)
            if fix and fix not in self.active_fixtures:
                self.active_fixtures.append(fix)

        for competition in self.tracked_competitions:
            fixtures = get_competition_fixtures(competition, date=date)
            self.active_fixtures.extend([
                f for f in fixtures if f not in self.active_fixtures
            ])

    def draw_fixtures(self, font_path, sorted=True, 
                      team_form_count=10, competition_form_count=0):
        if sorted:
            self.active_fixtures.sort( 
                key=lambda fix: (fix.datetime, fix.home_team.name)
            )

        while self.active_fixtures:
            current = self.active_fixtures.pop(0)

            # Only put form in for matches involving teams we're specifically tracking
            if current.home_team.id in self.tracked_teams or current.away_team.id in self.tracked_teams:
                form_count = team_form_count
            else:
                form_count = competition_form_count

            yield current.draw_card(font_path=font_path, form_count=form_count)

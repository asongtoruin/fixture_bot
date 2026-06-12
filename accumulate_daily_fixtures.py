from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.api import API
from src.drawing_tools.card import FixtureCard
from src.output_models import TeamInfo, League


def accumulate_daily_fixtures(tracking_folder: Path = Path("tracked")):
    # Load in the teams we want to track
    teams_folder = tracking_folder / "teams"
    with_form = [TeamInfo.from_file(f) for f in (teams_folder / "with_form").glob("*.json")]
    no_form = [TeamInfo.from_file(f) for f in (teams_folder / "no_form").glob("*.json")]

    leagues_folder = tracking_folder / "leagues"
    leagues = [League.from_file(f) for f in leagues_folder.glob("*.json")]

    # Set up the API object
    api = API()
    # Get today and tomorrow's fixtures, and loop through to figure out what to draw
    now = datetime.now()
    now_timestamp = now.astimezone(timezone.utc).timestamp()
    tomorrow = now + timedelta(days=1)
    tomorrow_timestamp = tomorrow.astimezone(timezone.utc).timestamp()

    today_fixtures = api.fixtures({"date": now.date()})
    tomorrow_fixtures = api.fixtures({"date": tomorrow.date()})
    cards_to_draw = []

    for fixture in today_fixtures.response + tomorrow_fixtures.response:
        # Skip any fixtures not in the next 24 hours
        if not (fixture.fixture.timestamp >= now_timestamp and fixture.fixture.timestamp < tomorrow_timestamp):
            continue
        playing_teams = (fixture.teams.home, fixture.teams.away)
        if any(team in playing_teams for team in with_form):
            home_form_resp = api.fixtures({"team": fixture.teams.home.id, "last": 10})
            away_form_resp = api.fixtures({"team": fixture.teams.away.id, "last": 10})

            # We want latest scores on the right!
            home_form = [f.result_for(fixture.teams.home).value for f in home_form_resp.response][::-1]
            away_form = [f.result_for(fixture.teams.away).value for f in away_form_resp.response][::-1]

            cards_to_draw.append(FixtureCard(fixture, home_form=home_form, away_form=away_form))

        elif any(team in playing_teams or fixture.league in leagues for team in no_form):
            cards_to_draw.append(FixtureCard(fixture))

    return cards_to_draw

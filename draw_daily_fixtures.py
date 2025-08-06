from datetime import datetime
from pathlib import Path

from src.api import API
from src.drawing_tools.card import FixtureCard
from src.output_models import TeamInfo


def draw_daily_fixtures(font_url: str, tracking_folder: Path = Path("tracked")):
    # Load in the teams we want to track
    teams_folder = tracking_folder / "teams"
    with_form = [TeamInfo.from_file(f) for f in (teams_folder / "with_form").glob("*.json")]
    no_form = [TeamInfo.from_file(f) for f in (teams_folder / "no_form").glob("*.json")]

    # Set up the API object
    api = API()

    # Get today's fixtures, and loop through to figure out what to draw
    active_fixtures = api.fixtures({"date": datetime.now().date})

    cards_to_draw = []

    for fixture in active_fixtures:
        playing_teams = (fixture.teams.home, fixture.teams.away)
        if any(team in playing_teams for team in with_form):
            home_form_resp = api.fixtures({"team": fixture.teams.home.id, "last": 10})
            away_form_resp = api.fixtures({"team": fixture.teams.away.id, "last": 10})

            # We want latest scores on the right!
            home_form = [f.result_for(fixture.teams.home).value for f in home_form_resp][::-1]
            away_form = [f.result_for(fixture.teams.away).value for f in away_form_resp][::-1]

            cards_to_draw.append(FixtureCard(fixture, home_form=home_form, away_form=away_form))

        elif any(team in playing_teams for team in no_form):
            cards_to_draw.append(FixtureCard(fixture))

    for card in cards_to_draw:
        yield card.draw(font_path=font_url)

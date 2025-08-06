import pytest

from src.input_models import FixturesInput
from src.output_models import FixturesResponse


@pytest.mark.vcr
def test_all_fixtures_by_date(api):
    params = FixturesInput(date="2025-08-07")

    resp = api.fixtures(params)

    assert isinstance(resp, FixturesResponse)


@pytest.mark.vcr
def test_team_last_fixtures(api):
    params = FixturesInput(team=1351, last=10)

    resp = api.fixtures(params)

    assert isinstance(resp, FixturesResponse)

import pytest

from src.input_models import TeamsInput
from src.output_models import TeamsResponse


@pytest.mark.vcr
def test_team_response(api):
    params = TeamsInput(name="Port Vale", country="England")

    resp = api.teams(params)

    assert isinstance(resp, TeamsResponse)

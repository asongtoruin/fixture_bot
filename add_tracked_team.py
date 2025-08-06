from argparse import ArgumentParser
from pathlib import Path

from src.api import API
from src.input_models import TeamsInput

parser = ArgumentParser(
    "Command-line utility for adding teams to track fixtures of"
)

parser.add_argument("team_name", type=str)
parser.add_argument("--team_country", type=str, default="England")
parser.add_argument("--include_form", type=bool, default=False)

args = parser.parse_args()

tracked_folder = Path("tracked/teams")

if args.include_form:
    tracked_folder = tracked_folder / "with_form"
else:
    tracked_folder = tracked_folder / "no_form"

tracked_folder.mkdir(exist_ok=True, parents=True)

params = TeamsInput(name=args.team_name, country=args.team_country)

api = API()
resp = api.teams(params)

resp.response[0].team.to_file(tracked_folder / f"{args.team_name}.json")

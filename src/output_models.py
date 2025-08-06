from datetime import datetime
from os import PathLike

from pydantic import BaseModel, HttpUrl


class FileIOModel(BaseModel):
    def to_file(self, file_path: PathLike):
        with open(file_path, "w") as output_path:
            output_path.write(self.model_dump_json(exclude_unset=True, indent=2))

    @classmethod
    def from_file(cls, file_path: PathLike):
        with open(file_path) as input_path:
            json_string = input_path.read()
        return cls.model_validate_json(json_string)


class Pagination(FileIOModel):
    current: int
    total: int


class BaseResponse(FileIOModel):
    get: str
    parameters: dict
    errors: list
    results: int
    paging: Pagination


class BasicTeam(FileIOModel):
    id: int
    name: str
    logo: HttpUrl

    def __eq__(self, other):
        if not isinstance(other, BasicTeam):
            return False
    
        return self.id == other.id


class TeamResult(BasicTeam):
    winner: bool | None


class TeamInfo(BasicTeam):
    code: str
    country: str
    founded: int
    national: bool


class MatchStatus(FileIOModel):
    long: str
    short: str
    elapsed: int | None


class SimpleVenue(FileIOModel):
    id: int | None
    name: str | None
    city: str | None


class VenueInfo(SimpleVenue):
    address: str
    capacity: int
    surface: str
    image: HttpUrl


class IndividualTeamResponse(FileIOModel):
    team: TeamInfo
    venue: VenueInfo


class League(FileIOModel):
    id: int
    name: str
    country: str
    logo: HttpUrl
    flag: HttpUrl | None
    season: int
    round: str


class Fixture(FileIOModel):
    id: int
    referee: str | None = None
    timezone: str
    date: datetime
    timestamp: int
    periods: dict
    venue: SimpleVenue
    status: MatchStatus


class FixtureTeams(FileIOModel):
    home: TeamResult
    away: TeamResult


class FixtureInfo(FileIOModel):
    fixture: Fixture
    league: League
    teams: FixtureTeams
    goals: dict
    score: dict


class TeamsResponse(BaseResponse):
    response: list[IndividualTeamResponse]


class FixturesResponse(BaseResponse):
    response: list[FixtureInfo]

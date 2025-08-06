from datetime import datetime
from os import PathLike

from pydantic import BaseModel, ConfigDict, HttpUrl

from src.utils import ResultsCode


class FileIOModel(BaseModel):
    # Allow extra terms in the responses - I may have missed something in my encoding!
    model_config = ConfigDict(
        extra="allow",
    )

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

    @property
    def finished(self) -> bool:
        return self.short in ("FT", "AET", "PEN")


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

    def result_for(self, team: BasicTeam) -> ResultsCode:
        if not self.fixture.status.finished:
            return ResultsCode.UNKNOWN
        
        if self.teams.home.winner is None:
            return ResultsCode.DRAW
        elif self.teams.home.winner:
            if self.teams.home == team:
                return ResultsCode.WIN
            else:
                return ResultsCode.LOSS
        else:
            if self.teams.away == team:
                return ResultsCode.WIN
            else:
                return ResultsCode.LOSS


class TeamsResponse(BaseResponse):
    response: list[IndividualTeamResponse]


class FixturesResponse(BaseResponse):
    response: list[FixtureInfo]

from os import PathLike

from pydantic import BaseModel, HttpUrl


class FileIOModel(BaseModel):
    def to_file(self, file_path: PathLike):
        with open(file_path, "w") as output_path:
            output_path.write(self.model_dump_json(exclude_unset=True, indent=2))


class Pagination(FileIOModel):
    current: int
    total: int


class BaseResponse(FileIOModel):
    get: str
    parameters: dict
    errors: list
    results: int
    paging: Pagination


class Team(FileIOModel):
    id: int
    name: str
    code: str
    country: str
    founded: int
    national: bool
    logo: HttpUrl


class Venue(FileIOModel):
    id: int
    name: str
    address: str
    city: str
    capacity: int
    surface: str
    image: HttpUrl


class IndividualTeamResponse(FileIOModel):
    team: Team
    venue: Venue


class TeamsResponse(BaseResponse):
    response: list[IndividualTeamResponse]

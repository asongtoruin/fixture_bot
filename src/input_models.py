from datetime import date

from pydantic import BaseModel, field_serializer, Field


class FixtureInput(BaseModel):
    id: int | None = None
    live: str | None = None
    date_: date | None = Field(serialization_alias="date", default=None)
    league: int | None = None
    season: int | None = Field(ge=1000, le=9999, default=None)
    team: int | None = None
    last: int | None = Field(ge=1, le=99, default=None)
    next_: int | None = Field(ge=1, le=99, default=None, serialization_alias="next")

    @field_serializer("date_")
    def _serialize_date(self, dt: date, _info):
        return dt.strftime("%Y-%m-%d")


class TeamsInput(BaseModel):
    id: int | None = None
    name: str | None = None
    league: int | None = None
    season: int | None = None
    country: str | None = None
    search: str | None = None
    code: str | None = None
    venue: int | None = None


if __name__ == "__main__":
    a = FixtureInput(date_="2024-01-01")
    print(a)

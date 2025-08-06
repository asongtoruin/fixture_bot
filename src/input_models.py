from datetime import date as dt_date

from pydantic import BaseModel, Field, field_serializer


class FixturesInput(BaseModel):
    id: int | None = None
    live: str | None = None
    date: dt_date | None = None
    league: int | None = None
    season: int | None = Field(ge=1000, le=9999, default=None)
    team: int | None = None
    last: int | None = Field(ge=1, le=99, default=None)
    next_: int | None = Field(ge=1, le=99, default=None, serialization_alias="next")

    @field_serializer("date")
    def _serialize_date(self, dt: dt_date, _info):
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
    a = FixturesInput(date_="2024-01-01")
    print(a)

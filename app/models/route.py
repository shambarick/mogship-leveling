from typing import List
from pydantic import BaseModel, Field


class SubmarineSector(BaseModel):
    name: str = Field(alias="Name")
    map_id: int = Field(alias="MapID")
    map_name: dict = Field(alias="Map")
    required_rank: int = Field(alias="Rank")
    sector_id: int = Field(alias="SectorId")
    alias_name: str = Field(alias="AliasName")
    exp: int = Field(alias="Exp")


class SubmarineRoute(BaseModel):
    required_rank: int = Field(alias="Rank")
    map_id: int = Field(alias="MapID")
    map_name: dict = Field(alias="Map")
    distance: int = Field(alias="Distance")
    sectors_total: int = Field(alias="SectorsTotal")
    exp: int = Field(alias="Exp")
    required_range: int = Field(alias="Range")
    route: List[int] = Field(alias="Route")
    route_details: List[SubmarineSector] = Field(alias="RouteDetails")

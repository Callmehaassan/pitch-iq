from pydantic import BaseModel
from typing import Optional
from datetime import date

# League Schemas
class LeagueBase(BaseModel):
    name: str
    country: str
    tier: int = 1

class LeagueCreate(LeagueBase):
    pass

class LeagueResponse(LeagueBase):
    league_id: int
    class Config:
        from_attributes = True

# Season Schemas
class SeasonBase(BaseModel):
    label: str
    start_date: date
    end_date: date

class SeasonCreate(SeasonBase):
    pass

class SeasonResponse(SeasonBase):
    season_id: int
    class Config:
        from_attributes = True

# Club Schemas
class ClubBase(BaseModel):
    name: str
    country: str

class ClubCreate(ClubBase):
    pass

class ClubResponse(ClubBase):
    club_id: int
    class Config:
        from_attributes = True

# Player Schemas
class PlayerBase(BaseModel):
    name: str
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    primary_position: Optional[str] = None

class PlayerCreate(PlayerBase):
    pass

class PlayerResponse(PlayerBase):
    player_id: int
    class Config:
        from_attributes = True

# TeamSeasonStats Schemas
class TeamSeasonStatsBase(BaseModel):
    club_id: int
    league_id: int
    season_id: int
    points: Optional[int] = None
    position: Optional[int] = None
    xG: Optional[float] = None
    xGA: Optional[float] = None
    possession: Optional[float] = None
    squad_value: Optional[float] = None
    matches_played: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None

class TeamSeasonStatsCreate(TeamSeasonStatsBase):
    pass

class TeamSeasonStatsResponse(TeamSeasonStatsBase):
    id: int
    class Config:
        from_attributes = True

# PlayerSeasonStats Schemas
class PlayerSeasonStatsBase(BaseModel):
    player_id: int
    season_id: int
    club_id: int
    league_id: int
    minutes: Optional[int] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    xG: Optional[float] = None
    xA: Optional[float] = None
    rating: Optional[float] = None

class PlayerSeasonStatsCreate(PlayerSeasonStatsBase):
    pass

class PlayerSeasonStatsResponse(PlayerSeasonStatsBase):
    id: int
    class Config:
        from_attributes = True

# Transfer Schemas
class TransferBase(BaseModel):
    player_id: int
    from_club_id: Optional[int] = None
    to_club_id: int
    season_id: int
    window: str

class TransferCreate(TransferBase):
    pass

class TransferResponse(TransferBase):
    transfer_id: int
    class Config:
        from_attributes = True

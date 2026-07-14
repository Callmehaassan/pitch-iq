from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.core import Player, PlayerSeasonStats, Season
from app.schemas.core import PlayerResponse
from typing import List, Optional

router = APIRouter(prefix="/players", tags=["Players"])

@router.get("/", response_model=List[PlayerResponse])
def get_players(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    league_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Player)

    if search:
        query = query.filter(Player.name.ilike(f"%{search}%"))

    if league_id:
        player_ids = db.query(PlayerSeasonStats.player_id).filter(
            PlayerSeasonStats.league_id == league_id
        ).distinct().subquery()
        query = query.filter(Player.player_id.in_(player_ids))

    return query.offset(skip).limit(limit).all()

@router.get("/count")
def get_players_count(
    search: Optional[str] = None,
    league_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Player)
    if search:
        query = query.filter(Player.name.ilike(f"%{search}%"))
    if league_id:
        player_ids = db.query(PlayerSeasonStats.player_id).filter(
            PlayerSeasonStats.league_id == league_id
        ).distinct().subquery()
        query = query.filter(Player.player_id.in_(player_ids))
    return {"count": query.count()}

@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.get("/{player_id}/stats")
def get_player_stats(player_id: int, db: Session = Depends(get_db)):
    stats = db.query(PlayerSeasonStats).filter(
        PlayerSeasonStats.player_id == player_id
    ).all()
    result = []
    for s in stats:
        season = db.query(Season).filter(Season.season_id == s.season_id).first()
        result.append({
            "id": s.id,
            "season_id": s.season_id,
            "season_label": season.label if season else f"Season {s.season_id}",
            "club_id": s.club_id,
            "minutes": s.minutes,
            "goals": s.goals,
            "assists": s.assists,
            "xG": s.xG,
            "xA": s.xA,
        })
    return result

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.core import League, Club, TeamSeasonStats
from app.schemas.core import LeagueResponse, ClubResponse, TeamSeasonStatsResponse
from typing import List

router = APIRouter(prefix="/leagues", tags=["Leagues"])

@router.get("/", response_model=List[LeagueResponse])
def get_leagues(db: Session = Depends(get_db)):
    return db.query(League).all()

@router.get("/{league_id}", response_model=LeagueResponse)
def get_league(league_id: int, db: Session = Depends(get_db)):
    league = db.query(League).filter(League.league_id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league

@router.get("/{league_id}/clubs", response_model=List[ClubResponse])
def get_league_clubs(league_id: int, season_id: int, db: Session = Depends(get_db)):
    stats = db.query(TeamSeasonStats).filter(
        TeamSeasonStats.league_id == league_id,
        TeamSeasonStats.season_id == season_id
    ).all()
    club_ids = [s.club_id for s in stats]
    return db.query(Club).filter(Club.club_id.in_(club_ids)).all()

@router.get("/{league_id}/standings")
def get_standings(league_id: int, season_id: int, db: Session = Depends(get_db)):
    stats = db.query(TeamSeasonStats).filter(
        TeamSeasonStats.league_id == league_id,
        TeamSeasonStats.season_id == season_id
    ).order_by(TeamSeasonStats.position).all()

    result = []
    for s in stats:
        club = db.query(Club).filter(Club.club_id == s.club_id).first()
        result.append({
            "id": s.id,
            "club_id": s.club_id,
            "club_name": club.name if club else f"Club {s.club_id}",
            "position": s.position,
            "points": s.points,
            "xG": s.xG,
            "xGA": s.xGA,
            "possession": s.possession,
            "wins": s.wins,
            "draws": s.draws,
            "losses": s.losses,
            "matches_played": s.matches_played,
        })
    return result

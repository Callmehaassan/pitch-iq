from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.core import Club, TeamSeasonStats, Player, PlayerSeasonStats
from app.schemas.prediction import (
    TeamPredictionResponse,
    PlayerPredictionResponse,
    NextSeasonLeagueResponse,
    NextSeasonAllLeaguesResponse,
)
from app.services.prediction_service import (
    predict_league_next_season,
    predict_all_leagues_next_season,
)
import joblib
import numpy as np
import os

router = APIRouter(prefix="/predict", tags=["Predictions"])

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "model_artifacts")

try:
    team_pts_model = joblib.load(os.path.join(MODEL_DIR, "team_points_model.pkl"))
    team_pos_model = joblib.load(os.path.join(MODEL_DIR, "team_position_model.pkl"))
    player_goals_model = joblib.load(os.path.join(MODEL_DIR, "player_goals_model.pkl"))
    MODELS_LOADED = True
except Exception as e:
    print(f"Warning: Could not load models: {e}")
    MODELS_LOADED = False

@router.get("/league/{club_id}", response_model=TeamPredictionResponse)
def predict_team(club_id: int, season_id: int, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.club_id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    stats = db.query(TeamSeasonStats).filter(
        TeamSeasonStats.club_id == club_id,
        TeamSeasonStats.season_id == season_id
    ).first()

    if not stats:
        raise HTTPException(status_code=404, detail="No stats found for this club and season")

    if MODELS_LOADED and stats.xG is not None:
        features = [[
            stats.xG or 0,
            stats.xGA or 0,
            stats.possession or 50,
            stats.wins or 0,
            stats.draws or 0,
            stats.losses or 0,
            stats.matches_played or 38,
            stats.league_id,
        ]]
        predicted_points = float(team_pts_model.predict(features)[0])
        predicted_position = int(round(float(team_pos_model.predict(features)[0])))
        predicted_position = max(1, min(20, predicted_position))
    else:
        predicted_points = float(stats.points or 50)
        predicted_position = stats.position or 10

    predicted_points = max(0, min(114, predicted_points))
    title_prob = round(max(0.001, min(0.99, 1 / max(1, predicted_position) * 0.5)), 3)
    top4_prob = round(max(0.01, min(0.99, 4 / max(1, predicted_position) * 0.4)), 3)
    rel_prob = round(max(0.001, min(0.99, max(0, predicted_position - 17) / 3 * 0.5)), 3)

    return TeamPredictionResponse(
        club_id=club_id,
        club_name=club.name,
        season_id=season_id,
        predicted_points=round(predicted_points, 1),
        predicted_position=predicted_position,
        title_probability=title_prob,
        top4_probability=top4_prob,
        relegation_probability=rel_prob,
        confidence_lower=round(predicted_points - 5, 1),
        confidence_upper=round(predicted_points + 5, 1),
        shap_features=[]
    )

@router.get("/next-season/{league_id}", response_model=NextSeasonLeagueResponse)
def predict_next_season_league(league_id: int, db: Session = Depends(get_db)):
    """Predict 2026/27 league standings using previous seasons of domestic performance."""
    result = predict_league_next_season(db, league_id)
    if not result["predictions"]:
        raise HTTPException(
            status_code=404,
            detail="No historical league data found. Run scrape_leagues.py and scrape_team_stats.py first.",
        )
    return result


@router.get("/next-season", response_model=NextSeasonAllLeaguesResponse)
def predict_next_season_all(db: Session = Depends(get_db)):
    """Predict 2026/27 winners for all tracked leagues from historical performance."""
    result = predict_all_leagues_next_season(db)
    if not result["leagues"]:
        raise HTTPException(
            status_code=404,
            detail="No historical league data found. Run scrape_leagues.py and scrape_team_stats.py first.",
        )
    return result


@router.get("/player/{player_id}", response_model=PlayerPredictionResponse)
def predict_player(player_id: int, season_id: int = 0, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    stats = db.query(PlayerSeasonStats).filter(
        PlayerSeasonStats.player_id == player_id
    ).order_by(PlayerSeasonStats.season_id.desc()).first()

    if MODELS_LOADED and stats and stats.minutes:
        features = [[
            stats.minutes or 0,
            stats.assists or 0,
            stats.xG or 0,
            stats.xA or 0,
            stats.league_id,
            stats.season_id,
        ]]
        predicted_goals = float(player_goals_model.predict(features)[0])
        predicted_goals = max(0, predicted_goals)
    else:
        predicted_goals = float(stats.goals or 0) if stats else 0.0

    predicted_assists = float(stats.assists or 0) if stats else 0.0
    predicted_minutes = float(stats.minutes or 0) if stats else 0.0

    return PlayerPredictionResponse(
        player_id=player_id,
        player_name=player.name,
        season_id=season_id,
        predicted_goals=round(predicted_goals, 1),
        predicted_assists=round(predicted_assists, 1),
        predicted_minutes=round(predicted_minutes, 0),
        predicted_rating=7.0,
        confidence_lower=round(max(0, predicted_goals - 3), 1),
        confidence_upper=round(predicted_goals + 3, 1),
        shap_features=[]
    )

from fastapi import APIRouter as _APIRouter
from app.database import SessionLocal as _SessionLocal
from app.models.core import TeamSeasonStats as _TSS, Club as _Club
import joblib as _joblib
import numpy as _np
import os as _os

_MODEL_PATH = _os.path.join(_os.path.dirname(__file__), "..", "..", "model_artifacts", "next_season_model.pkl")

@router.get("/next-season/{league_id}")
def predict_next_season(league_id: int):
    try:
        model = _joblib.load(_MODEL_PATH)
    except Exception as e:
        return {"error": f"Model not loaded: {e}"}

    db = _SessionLocal()
    try:
        # Get the most recent season for this league
        latest = db.query(_TSS).filter(
            _TSS.league_id == league_id,
            _TSS.points != None,
            _TSS.points > 0
        ).order_by(_TSS.season_id.desc()).first()

        if not latest:
            return {"error": "No data found for this league"}

        latest_season_id = latest.season_id

        # Get only teams that played in the most recent season
        latest_teams = db.query(_TSS).filter(
            _TSS.league_id == league_id,
            _TSS.season_id == latest_season_id,
            _TSS.points != None,
            _TSS.points > 0
        ).all()

        current_club_ids = [t.club_id for t in latest_teams]

        # For each current team get all their historical seasons
        all_rows = db.query(_TSS).filter(
            _TSS.league_id == league_id,
            _TSS.club_id.in_(current_club_ids),
            _TSS.points != None,
            _TSS.points > 0
        ).all()

        club_seasons = {}
        for r in all_rows:
            if r.club_id not in club_seasons:
                club_seasons[r.club_id] = []
            club_seasons[r.club_id].append(r)

        predictions = []
        for club_id in current_club_ids:
            seasons = club_seasons.get(club_id, [])
            if not seasons:
                continue

            seasons_sorted = sorted(seasons, key=lambda x: x.season_id)
            avg_points = _np.mean([s.points for s in seasons_sorted])
            avg_xG = _np.mean([s.xG or 0 for s in seasons_sorted])
            avg_xGA = _np.mean([s.xGA or 0 for s in seasons_sorted])
            avg_possession = _np.mean([s.possession or 50 for s in seasons_sorted])
            avg_wins = _np.mean([s.wins or 0 for s in seasons_sorted])
            trend = seasons_sorted[-1].points - seasons_sorted[-2].points if len(seasons_sorted) >= 2 else 0
            last_pts = seasons_sorted[-1].points
            last_xG = seasons_sorted[-1].xG or 0
            last_xGA = seasons_sorted[-1].xGA or 0
            num_seasons = len(seasons_sorted)

            feat = [[avg_points, avg_xG, avg_xGA, avg_possession, avg_wins,
                     trend, last_pts, last_xG, last_xGA, num_seasons, league_id]]
            pred_pts = float(model.predict(feat)[0])
            pred_pts = max(10, min(110, pred_pts))

            club = db.query(_Club).filter(_Club.club_id == club_id).first()
            predictions.append({
                "club_id": club_id,
                "club_name": club.name if club else f"Club {club_id}",
                "predicted_points": round(pred_pts, 1),
                "last_season_points": last_pts,
                "trend": round(trend, 1),
                "seasons_used": num_seasons,
            })

        predictions.sort(key=lambda x: -x["predicted_points"])
        for i, p in enumerate(predictions, 1):
            p["predicted_position"] = i

        return {
            "league_id": league_id,
            "season": "2026/27",
            "based_on_season_id": latest_season_id,
            "predictions": predictions
        }
    finally:
        db.close()

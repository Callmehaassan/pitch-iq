from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.prediction import UCLPredictionResponse
from app.services.prediction_service import (
    get_team_strengths_from_leagues,
    simulate_ucl_tournament,
)

router = APIRouter(prefix="/api/ucl", tags=["ucl"])


@router.get("/team-strengths")
def get_team_strengths(db: Session = Depends(get_db)):
    """Team strength rankings from domestic league performance (points, xG, form)."""
    return get_team_strengths_from_leagues(db)


@router.get("/predict", response_model=UCLPredictionResponse)
def predict_ucl_winner(
    iterations: int = Query(default=1000, ge=100, le=10000),
    db: Session = Depends(get_db),
):
    """Predict UCL 2026/27 winner using Monte Carlo simulation on league-derived team strengths."""
    result = simulate_ucl_tournament(db, iterations=iterations)
    return {
        "target_season": result["target_season"],
        "participants": result["participants"],
        "predicted_winner": result.get("predicted_winner"),
        "winner_probabilities": result["winner_probabilities"],
        "iterations": result["iterations"],
        "data_source": result["data_source"],
        "message": result.get("message"),
    }


@router.post("/simulate")
def simulate_ucl_bracket(
    iterations: int = Query(default=1000, ge=100, le=10000),
    db: Session = Depends(get_db),
):
    """Run UCL bracket simulation using real league performance data."""
    result = simulate_ucl_tournament(db, iterations=iterations)
    return {
        "target_season": result["target_season"],
        "participants": result["participants"],
        "predicted_winner": result.get("predicted_winner"),
        "winner_probabilities": result["winner_probabilities"],
        "bracket": result.get("sample_bracket"),
        "iterations": result["iterations"],
        "data_source": result["data_source"],
        "message": result.get("message"),
    }

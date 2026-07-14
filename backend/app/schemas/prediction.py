from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PredictionLogResponse(BaseModel):
    prediction_id: str
    entity_type: str
    entity_id: int
    season_id: int
    prediction_type: str
    predicted_value: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    model_version: str
    created_at: datetime
    resolved_actual: Optional[float] = None
    data_quality: Optional[str] = None
    cold_start: bool = False

    class Config:
        from_attributes = True

class PredictionExplanationResponse(BaseModel):
    explanation_id: str
    prediction_id: str
    feature_name: str
    shap_value: float
    rank: int

    class Config:
        from_attributes = True

class TeamPredictionResponse(BaseModel):
    club_id: int
    club_name: str
    season_id: int
    predicted_points: float
    predicted_position: int
    title_probability: float
    top4_probability: float
    relegation_probability: float
    confidence_lower: float
    confidence_upper: float
    data_quality: Optional[str] = None
    cold_start: bool = False
    shap_features: list[PredictionExplanationResponse] = []

class PlayerPredictionResponse(BaseModel):
    player_id: int
    player_name: str
    season_id: int
    predicted_goals: float
    predicted_assists: float
    predicted_minutes: float
    predicted_rating: float
    confidence_lower: float
    confidence_upper: float
    shap_features: list[PredictionExplanationResponse] = []


class NextSeasonClubPrediction(BaseModel):
    club_id: int
    club_name: str
    league_id: int
    predicted_points: float
    predicted_position: int
    title_probability: float
    strength: float
    last_season_points: float
    last_season_position: int
    seasons_used: int
    form_trend: float


class NextSeasonLeagueResponse(BaseModel):
    league_id: int
    league_name: str
    target_season: str
    predicted_winner: Optional[str] = None
    predictions: list[NextSeasonClubPrediction]
    data_source: str


class NextSeasonAllLeaguesResponse(BaseModel):
    target_season: str
    leagues: list[NextSeasonLeagueResponse]
    data_source: str


class UCLWinnerProbability(BaseModel):
    club_name: str
    win_probability: float
    win_percentage: float


class UCLParticipant(BaseModel):
    club_id: int
    club_name: str
    league_id: int
    league_name: str
    strength: float
    predicted_points_2026_27: float
    last_position: int
    last_points: float
    seasons_used: int


class UCLPredictionResponse(BaseModel):
    target_season: str
    participants: list[UCLParticipant]
    predicted_winner: Optional[str] = None
    winner_probabilities: list[UCLWinnerProbability]
    iterations: int
    data_source: str
    message: Optional[str] = None

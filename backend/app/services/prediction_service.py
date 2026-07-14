"""Prediction engine using historical league performance data."""

from __future__ import annotations

import os
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
from sqlalchemy.orm import Session

from app.models.core import Club, TeamSeasonStats

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "model_artifacts")
TARGET_SEASON_LABEL = "2026/27"

LEAGUE_NAMES = {
    1: "ENG-Premier League",
    2: "ESP-La Liga",
    3: "GER-Bundesliga",
    4: "ITA-Serie A",
    5: "FRA-Ligue 1",
}

# UEFA coefficient-style weighting for cross-league comparison
LEAGUE_COEFFICIENTS = {
    1: 1.00,
    2: 0.96,
    3: 0.92,
    4: 0.90,
    5: 0.86,
}

FEATURE_COLUMNS = [
    "avg_points", "avg_xG", "avg_xGA", "avg_possession",
    "avg_wins", "trend_points", "last_points", "last_xG",
    "last_xGA", "num_seasons", "league_id",
]


@dataclass
class SeasonSnapshot:
    season_id: int
    league_id: int
    points: float
    xG: float
    xGA: float
    possession: float
    wins: float
    draws: float
    losses: float
    matches_played: float
    position: float


def _season_dict(row: TeamSeasonStats) -> SeasonSnapshot:
    return SeasonSnapshot(
        season_id=row.season_id,
        league_id=row.league_id,
        points=float(row.points or 0),
        xG=float(row.xG or 0),
        xGA=float(row.xGA or 0),
        possession=float(row.possession or 50),
        wins=float(row.wins or 0),
        draws=float(row.draws or 0),
        losses=float(row.losses or 0),
        matches_played=float(row.matches_played or 38),
        position=float(row.position or 10),
    )


def build_club_history(db: Session) -> dict[int, list[SeasonSnapshot]]:
    rows = db.query(TeamSeasonStats).filter(TeamSeasonStats.points.isnot(None)).all()
    history: dict[int, list[SeasonSnapshot]] = defaultdict(list)
    for row in rows:
        history[row.club_id].append(_season_dict(row))
    # Map season_id to year for correct chronological sorting
    SEASON_ID_TO_YEAR = {1: 2024, 2: 2023, 3: 2022, 4: 2020, 5: 2021, 6: 2025}
    for club_id in history:
        history[club_id].sort(key=lambda s: SEASON_ID_TO_YEAR.get(s.season_id, s.season_id))
    return dict(history)


def _load_next_season_model():
    model_path = os.path.join(MODEL_DIR, "next_season_model.pkl")
    features_path = os.path.join(MODEL_DIR, "next_season_features.pkl")
    if not os.path.exists(model_path):
        return None, FEATURE_COLUMNS
    try:
        model = joblib.load(model_path)
        features = joblib.load(features_path) if os.path.exists(features_path) else FEATURE_COLUMNS
        return model, features
    except Exception:
        return None, FEATURE_COLUMNS


def _build_features(seasons: list[SeasonSnapshot]) -> dict[str, float]:
    n = len(seasons)
    weights = np.array([1.5 ** i for i in range(n)])
    weights = weights / weights.sum()
    avg_points = float(np.average([s.points for s in seasons], weights=weights))
    avg_xG = float(np.average([s.xG for s in seasons], weights=weights))
    avg_xGA = float(np.average([s.xGA for s in seasons], weights=weights))
    avg_possession = float(np.average([s.possession for s in seasons], weights=weights))
    avg_wins = float(np.average([s.wins for s in seasons], weights=weights))
    trend_points = seasons[-1].points - seasons[-2].points if len(seasons) >= 2 else 0.0
    last = seasons[-1]
    return {
        "avg_points": avg_points,
        "avg_xG": avg_xG,
        "avg_xGA": avg_xGA,
        "avg_possession": avg_possession,
        "avg_wins": avg_wins,
        "trend_points": trend_points,
        "last_points": last.points,
        "last_xG": last.xG,
        "last_xGA": last.xGA,
        "num_seasons": float(len(seasons)),
        "league_id": float(last.league_id),
    }


def predict_next_season_points(seasons: list[SeasonSnapshot]) -> float:
    """Predict points for next season using weighted historical average."""
    if not seasons:
        return 40.0
    n = len(seasons)
    weights = np.array([1.8 ** i for i in range(n)], dtype=float)
    weights = weights / weights.sum()
    weighted_pts = float(np.average([s.points for s in seasons], weights=weights))
    trend = seasons[-1].points - seasons[-2].points if n >= 2 else 0
    trend_factor = trend * 0.15
    predicted = weighted_pts + trend_factor
    return float(max(15, min(105, predicted)))


def compute_team_strength(seasons: list[SeasonSnapshot]) -> float:
    """Composite strength score from domestic league performance."""
    if not seasons:
        return 30.0

    latest = seasons[-1]
    avg_points = float(np.mean([s.points for s in seasons]))
    avg_xg = float(np.mean([s.xG for s in seasons]))
    avg_xga = float(np.mean([s.xGA for s in seasons]))
    xg_diff = (latest.xG or avg_xg) - (latest.xGA or avg_xga)
    form = latest.points - avg_points if len(seasons) > 1 else 0.0
    position_factor = 20.0 / max(1.0, latest.position)
    win_rate = latest.wins / max(1.0, latest.matches_played)

    raw = (
        latest.points * 0.30
        + avg_points * 0.20
        + xg_diff * 4.0 * 0.20
        + position_factor * 0.15
        + form * 0.10
        + win_rate * 38.0 * 0.05
    )
    coeff = LEAGUE_COEFFICIENTS.get(latest.league_id, 0.85)
    return round(raw * coeff, 3)


def _softmax_title_probabilities(predictions: list[dict[str, Any]], n_sims: int = 5000) -> None:
    """Monte Carlo title probabilities from predicted points + historical variance."""
    if not predictions:
        return

    points = np.array([p["predicted_points"] for p in predictions], dtype=float)
    std = max(6.0, float(np.std(points)) * 0.35)
    wins: dict[int, int] = defaultdict(int)

    for _ in range(n_sims):
        noisy = points + np.random.normal(0, std, len(points))
        winner_idx = int(np.argmax(noisy))
        wins[predictions[winner_idx]["club_id"]] += 1

    for p in predictions:
        p["title_probability"] = round(wins[p["club_id"]] / n_sims, 4)


def predict_league_next_season(
    db: Session,
    league_id: int,
) -> dict[str, Any]:
    history = build_club_history(db)
    predictions: list[dict[str, Any]] = []

    # Find the most recent season_id for this league
    all_league_rows = db.query(TeamSeasonStats).filter(
        TeamSeasonStats.league_id == league_id,
        TeamSeasonStats.points.isnot(None),
        TeamSeasonStats.points > 0
    ).order_by(TeamSeasonStats.season_id.desc()).first()

    if not all_league_rows:
        return {"league_id": league_id, "league_name": LEAGUE_NAMES.get(league_id, ""), "target_season": TARGET_SEASON_LABEL, "predicted_winner": None, "predictions": [], "data_source": "historical_league_performance"}

    latest_season_id = all_league_rows.season_id

    # Get only clubs that played in the most recent season
    current_clubs = db.query(TeamSeasonStats.club_id).filter(
        TeamSeasonStats.league_id == league_id,
        TeamSeasonStats.season_id == latest_season_id,
        TeamSeasonStats.points.isnot(None),
        TeamSeasonStats.points > 0
    ).all()
    current_club_ids = {row.club_id for row in current_clubs}

    for club_id, seasons in history.items():
        if club_id not in current_club_ids:
            continue
        league_seasons = [s for s in seasons if s.league_id == league_id]
        if not league_seasons:
            continue

        club = db.query(Club).filter(Club.club_id == club_id).first()
        pred_pts = predict_next_season_points(league_seasons)
        strength = compute_team_strength(league_seasons)
        latest = league_seasons[-1]

        predictions.append({
            "club_id": club_id,
            "club_name": club.name if club else f"Club {club_id}",
            "league_id": league_id,
            "predicted_points": round(pred_pts, 1),
            "strength": strength,
            "last_season_points": latest.points,
            "last_season_position": int(latest.position),
            "seasons_used": len(league_seasons),
            "form_trend": round(latest.points - league_seasons[-2].points, 1) if len(league_seasons) >= 2 else 0.0,
        })

    predictions.sort(key=lambda x: x["predicted_points"], reverse=True)
    for i, p in enumerate(predictions, 1):
        p["predicted_position"] = i

    _softmax_title_probabilities(predictions)

    return {
        "league_id": league_id,
        "league_name": LEAGUE_NAMES.get(league_id, f"League {league_id}"),
        "target_season": TARGET_SEASON_LABEL,
        "predicted_winner": predictions[0]["club_name"] if predictions else None,
        "predictions": predictions,
        "data_source": "historical_league_performance",
    }


def predict_all_leagues_next_season(db: Session) -> dict[str, Any]:
    results = []
    for league_id in sorted(LEAGUE_NAMES.keys()):
        league_pred = predict_league_next_season(db, league_id)
        if league_pred["predictions"]:
            results.append(league_pred)

    return {
        "target_season": TARGET_SEASON_LABEL,
        "leagues": results,
        "data_source": "historical_league_performance",
    }


def select_ucl_participants(db: Session, count: int = 16) -> list[dict[str, Any]]:
    """Pick UCL teams from domestic league performance (top clubs by strength)."""
    history = build_club_history(db)
    candidates: list[dict[str, Any]] = []

    for club_id, seasons in history.items():
        if not seasons:
            continue
        latest = seasons[-1]
        club = db.query(Club).filter(Club.club_id == club_id).first()
        strength = compute_team_strength(seasons)
        next_pts = predict_next_season_points(seasons)

        candidates.append({
            "club_id": club_id,
            "club_name": club.name if club else f"Club {club_id}",
            "league_id": latest.league_id,
            "league_name": LEAGUE_NAMES.get(latest.league_id, ""),
            "strength": strength,
            "predicted_points_2026_27": round(next_pts, 1),
            "last_position": int(latest.position),
            "last_points": latest.points,
            "seasons_used": len(seasons),
        })

    candidates.sort(key=lambda x: x["strength"], reverse=True)
    return candidates[:count]


def _simulate_knockout_match(
    home: dict[str, Any],
    away: dict[str, Any],
    home_advantage: float = 1.06,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    home_eff = home["strength"] * home_advantage
    away_eff = away["strength"]
    total = max(home_eff + away_eff, 1.0)

    total_eff = home_eff + away_eff
    home_share = home_eff / total_eff
    away_share = away_eff / total_eff
    match_total_goals = max(1.5, min(4.5, (home_eff + away_eff) / 22.0))
    home_xg = max(0.4, home_share * match_total_goals * 1.05)
    away_xg = max(0.4, away_share * match_total_goals * 0.95)
    home_goals = int(np.random.poisson(home_xg))
    away_goals = int(np.random.poisson(away_xg))

    if home_goals == away_goals:
        home_wins = random.random() < home_eff / total
        if home_wins:
            home_goals += 1
        else:
            away_goals += 1

    home_win_prob = round(home_eff / total * 100, 1)
    away_win_prob = round(100 - home_win_prob, 1)

    home_out = {
        "name": home["club_name"],
        "score": home_goals,
        "xG": round(home_xg, 2),
        "winProb": home_win_prob,
        "strength": home["strength"],
    }
    away_out = {
        "name": away["club_name"],
        "score": away_goals,
        "xG": round(away_xg, 2),
        "winProb": away_win_prob,
        "strength": away["strength"],
    }
    winner = home_out if home_goals > away_goals else away_out
    return home_out, away_out, winner


def _run_single_bracket(teams: list[dict[str, Any]]) -> dict[str, Any]:
    shuffled = teams.copy()
    random.shuffle(shuffled)

    def play_round(pairings: list[tuple[dict, dict]]) -> list[dict[str, Any]]:
        matches = []
        for home, away in pairings:
            h, a, w = _simulate_knockout_match(home, away)
            matches.append({"home": h, "away": a, "winner": w, "played": True})
        return matches

    r16_pairs = [(shuffled[i], shuffled[i + 1]) for i in range(0, 16, 2)]
    r16 = play_round(r16_pairs)

    qf_pairs = [
        ({"club_name": r16[i]["winner"]["name"], "strength": r16[i]["winner"]["strength"]},
         {"club_name": r16[i + 1]["winner"]["name"], "strength": r16[i + 1]["winner"]["strength"]})
        for i in range(0, 8, 2)
    ]
    qf = play_round(qf_pairs)

    sf_pairs = [
        ({"club_name": qf[i]["winner"]["name"], "strength": qf[i]["winner"]["strength"]},
         {"club_name": qf[i + 1]["winner"]["name"], "strength": qf[i + 1]["winner"]["strength"]})
        for i in range(0, 4, 2)
    ]
    sf = play_round(sf_pairs)

    final_h, final_a, final_w = _simulate_knockout_match(
        {"club_name": sf[0]["winner"]["name"], "strength": sf[0]["winner"]["strength"]},
        {"club_name": sf[1]["winner"]["name"], "strength": sf[1]["winner"]["strength"]},
        home_advantage=1.0,
    )
    final = {"home": final_h, "away": final_a, "winner": final_w, "played": True}

    return {"r16": r16, "qf": qf, "sf": sf, "final": final}


def simulate_ucl_tournament(
    db: Session,
    iterations: int = 1000,
) -> dict[str, Any]:
    """Monte Carlo UCL simulation using domestic league performance data."""
    participants = select_ucl_participants(db, count=16)
    if len(participants) < 2:
        return {
            "target_season": TARGET_SEASON_LABEL,
            "participants": participants,
            "winner_probabilities": [],
            "sample_bracket": None,
            "iterations": 0,
            "data_source": "historical_league_performance",
            "message": "Not enough team data. Run the data scrapers first.",
        }

    win_counts: dict[str, int] = defaultdict(int)
    actual_iters = min(max(iterations, 100), 10000)

    for _ in range(actual_iters):
        bracket = _run_single_bracket(participants)
        win_counts[bracket["final"]["winner"]["name"]] += 1

    winner_probs = [
        {
            "club_name": name,
            "win_probability": round(count / actual_iters, 4),
            "win_percentage": round(count / actual_iters * 100, 1),
        }
        for name, count in win_counts.items()
    ]
    winner_probs.sort(key=lambda x: x["win_probability"], reverse=True)

    sample_bracket = _run_single_bracket(participants)

    return {
        "target_season": TARGET_SEASON_LABEL,
        "participants": participants,
        "predicted_winner": winner_probs[0]["club_name"] if winner_probs else None,
        "winner_probabilities": winner_probs,
        "sample_bracket": sample_bracket,
        "iterations": actual_iters,
        "data_source": "historical_league_performance",
    }


def get_team_strengths_from_leagues(db: Session) -> dict[str, Any]:
    """Team strength rankings derived from domestic league stats."""
    history = build_club_history(db)
    teams: list[dict[str, Any]] = []

    for club_id, seasons in history.items():
        if not seasons:
            continue
        club = db.query(Club).filter(Club.club_id == club_id).first()
        latest = seasons[-1]
        teams.append({
            "club_id": club_id,
            "team": club.name if club else f"Club {club_id}",
            "league_id": latest.league_id,
            "league_name": LEAGUE_NAMES.get(latest.league_id, ""),
            "strength": compute_team_strength(seasons),
            "last_points": latest.points,
            "last_position": int(latest.position),
            "last_xG": latest.xG,
            "last_xGA": latest.xGA,
            "predicted_points_2026_27": round(predict_next_season_points(seasons), 1),
            "seasons_used": len(seasons),
        })

    teams.sort(key=lambda x: x["strength"], reverse=True)
    return {
        "teams": teams,
        "total": len(teams),
        "target_season": TARGET_SEASON_LABEL,
        "data_source": "historical_league_performance",
    }

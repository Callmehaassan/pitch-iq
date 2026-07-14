import pandas as pd
import numpy as np
from app.database import SessionLocal
from app.models.core import TeamSeasonStats, Club, Season, League
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

os.makedirs("model_artifacts", exist_ok=True)
db = SessionLocal()

print("Building multi-season prediction model...")

rows = db.query(TeamSeasonStats).filter(
    TeamSeasonStats.points != None,
    TeamSeasonStats.xG != None,
).all()

club_season_data = {}
for r in rows:
    key = r.club_id
    if key not in club_season_data:
        club_season_data[key] = []
    club_season_data[key].append({
        "season_id": r.season_id,
        "league_id": r.league_id,
        "points": r.points or 0,
        "xG": r.xG or 0,
        "xGA": r.xGA or 0,
        "possession": r.possession or 50,
        "wins": r.wins or 0,
        "draws": r.draws or 0,
        "losses": r.losses or 0,
        "matches_played": r.matches_played or 38,
        "position": r.position or 10,
    })

training_data = []
for club_id, seasons in club_season_data.items():
    SEASON_ID_TO_YEAR = {1: 2024, 2: 2023, 3: 2022, 4: 2020, 5: 2021, 6: 2025}
    seasons_sorted = sorted(seasons, key=lambda x: SEASON_ID_TO_YEAR.get(x["season_id"], x["season_id"]))
    for i in range(1, len(seasons_sorted)):
        prev_seasons = seasons_sorted[:i]
        current = seasons_sorted[i]

        # Weight recent seasons more heavily
        n = len(prev_seasons)
        weights = np.array([1.5 ** i for i in range(n)])
        weights = weights / weights.sum()
        avg_points = float(np.average([s["points"] for s in prev_seasons], weights=weights))
        avg_xG = float(np.average([s["xG"] for s in prev_seasons], weights=weights))
        avg_xGA = float(np.average([s["xGA"] for s in prev_seasons], weights=weights))
        avg_possession = float(np.average([s["possession"] for s in prev_seasons], weights=weights))
        avg_wins = float(np.average([s["wins"] for s in prev_seasons], weights=weights))
        trend_points = seasons_sorted[i-1]["points"] - seasons_sorted[max(0,i-2)]["points"] if i >= 2 else 0
        last_points = seasons_sorted[i-1]["points"]
        last_xG = seasons_sorted[i-1]["xG"]
        last_xGA = seasons_sorted[i-1]["xGA"]
        num_seasons = len(prev_seasons)

        training_data.append({
            "club_id": club_id,
            "league_id": current["league_id"],
            "avg_points": avg_points,
            "avg_xG": avg_xG,
            "avg_xGA": avg_xGA,
            "avg_possession": avg_possession,
            "avg_wins": avg_wins,
            "trend_points": trend_points,
            "last_points": last_points,
            "last_xG": last_xG,
            "last_xGA": last_xGA,
            "num_seasons": num_seasons,
            "target_points": current["points"],
            "target_position": current["position"],
        })

df = pd.DataFrame(training_data)
print(f"Training rows: {len(df)}")

if len(df) < 10:
    print("Not enough multi-season data yet. Run after more seasons are scraped.")
    db.close()
    exit()

features = [
    "avg_points", "avg_xG", "avg_xGA", "avg_possession",
    "avg_wins", "trend_points", "last_points", "last_xG",
    "last_xGA", "num_seasons", "league_id"
]

X = df[features]
y_pts = df["target_points"]

X_train, X_test, y_train, y_test = train_test_split(X, y_pts, test_size=0.2, random_state=42)
model = xgb.XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.05, random_state=42)
model.fit(X_train, y_train)
preds = model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test, preds):.2f} points")
print(f"R2: {r2_score(y_test, preds):.3f}")

joblib.dump(model, "model_artifacts/next_season_model.pkl")
joblib.dump(features, "model_artifacts/next_season_features.pkl")
print("Model saved!")

print("\n=== 2026/27 PREDICTIONS ===")
all_clubs = db.query(TeamSeasonStats).filter(TeamSeasonStats.points != None).all()
club_ids = list(set([r.club_id for r in all_clubs]))

predictions = []
for club_id in club_ids:
    seasons = club_season_data.get(club_id, [])
    if len(seasons) < 2:
        continue

    SEASON_ID_TO_YEAR = {1: 2024, 2: 2023, 3: 2022, 4: 2020, 5: 2021, 6: 2025}
    seasons_sorted = sorted(seasons, key=lambda x: SEASON_ID_TO_YEAR.get(x["season_id"], x["season_id"]))
    avg_points = np.mean([s["points"] for s in seasons_sorted])
    avg_xG = np.mean([s["xG"] for s in seasons_sorted])
    avg_xGA = np.mean([s["xGA"] for s in seasons_sorted])
    avg_possession = np.mean([s["possession"] for s in seasons_sorted])
    avg_wins = np.mean([s["wins"] for s in seasons_sorted])
    trend_points = seasons_sorted[-1]["points"] - seasons_sorted[-2]["points"]
    last_points = seasons_sorted[-1]["points"]
    last_xG = seasons_sorted[-1]["xG"]
    last_xGA = seasons_sorted[-1]["xGA"]
    num_seasons = len(seasons_sorted)
    league_id = seasons_sorted[-1]["league_id"]

    feat = [[avg_points, avg_xG, avg_xGA, avg_possession, avg_wins,
             trend_points, last_points, last_xG, last_xGA, num_seasons, league_id]]
    pred_pts = float(model.predict(feat)[0])

    club = db.query(Club).filter(Club.club_id == club_id).first()
    predictions.append({
        "club_id": club_id,
        "club_name": club.name if club else f"Club {club_id}",
        "league_id": league_id,
        "predicted_points_2026_27": round(pred_pts, 1),
    })

df_pred = pd.DataFrame(predictions)
for league_id in sorted(df_pred["league_id"].unique()):
    league_name = {1:"EPL", 2:"La Liga", 3:"Bundesliga", 4:"Serie A", 5:"Ligue 1"}.get(league_id, f"League {league_id}")
    print(f"\n{league_name} 2026/27 Predictions:")
    league_df = df_pred[df_pred["league_id"] == league_id].sort_values("predicted_points_2026_27", ascending=False)
    for i, row in enumerate(league_df.itertuples(), 1):
        print(f"  {i}. {row.club_name}: {row.predicted_points_2026_27} pts")

db.close()

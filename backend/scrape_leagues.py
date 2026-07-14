import soccerdata as sd
import pandas as pd
from app.database import SessionLocal
from app.models.core import League, Season, Club, TeamSeasonStats
from datetime import date

db = SessionLocal()

LEAGUES = {
    "ENG-Premier League": 1,
    "ESP-La Liga": 2,
    "GER-Bundesliga": 3,
    "ITA-Serie A": 4,
    "FRA-Ligue 1": 5,
}

SEASONS = [
    ("2020/21", "20-21", date(2020,8,1), date(2021,5,31)),
    ("2021/22", "21-22", date(2021,8,1), date(2022,5,31)),
    ("2022/23", "22-23", date(2022,8,1), date(2023,5,31)),
    ("2023/24", "23-24", date(2023,8,1), date(2024,5,31)),
    ("2024/25", "24-25", date(2024,8,1), date(2025,5,31)),
]

season_ids = {}
for label, sd_season, start, end in SEASONS:
    existing = db.query(Season).filter(Season.label == label).first()
    if not existing:
        s = Season(label=label, start_date=start, end_date=end)
        db.add(s)
        db.flush()
        season_ids[sd_season] = s.season_id
    else:
        season_ids[sd_season] = existing.season_id

db.commit()
print("Seasons ready")

for league_str, league_id in LEAGUES.items():
    print(f"Scraping {league_str}...")
    for sd_season, season_id in season_ids.items():
        try:
            fbref = sd.FBref(leagues=league_str, seasons=sd_season)
            stats = fbref.read_team_season_stats(stat_type="standard")
            stats = stats.reset_index()
            print(f"  Got {len(stats)} rows for {sd_season}")

            for _, row in stats.iterrows():
                try:
                    club_name = str(row.get("team", "Unknown"))
                    club = db.query(Club).filter(Club.name == club_name).first()
                    if not club:
                        club = Club(name=club_name, country=league_str.split("-")[0])
                        db.add(club)
                        db.flush()

                    existing_stat = db.query(TeamSeasonStats).filter(
                        TeamSeasonStats.club_id == club.club_id,
                        TeamSeasonStats.league_id == league_id,
                        TeamSeasonStats.season_id == season_id
                    ).first()

                    if not existing_stat:
                        stat = TeamSeasonStats(
                            club_id=club.club_id,
                            league_id=league_id,
                            season_id=season_id,
                            matches_played=int(row.get("MP", 0) or 0),
                            wins=int(row.get("W", 0) or 0),
                            draws=int(row.get("D", 0) or 0),
                            losses=int(row.get("L", 0) or 0),
                            points=int(row.get("Pts", 0) or 0),
                        )
                        db.add(stat)
                except Exception as e:
                    print(f"    Row error: {e}")
                    continue

            db.commit()
            print(f"  Saved {league_str} {sd_season}")
        except Exception as e:
            print(f"  Failed {league_str} {sd_season}: {e}")

db.close()
print("All done!")

import soccerdata as sd
from app.database import SessionLocal
from app.models.core import Player, PlayerSeasonStats, Club, Season
import time
import sys

db = SessionLocal()

LEAGUES = {
    "epl": ("ENG-Premier League", 1),
    "laliga": ("ESP-La Liga", 2),
    "bundesliga": ("GER-Bundesliga", 3),
    "seriea": ("ITA-Serie A", 4),
    "ligue1": ("FRA-Ligue 1", 5),
}

SEASONS = {
    "20-21": "2020/21",
    "21-22": "2021/22",
    "22-23": "2022/23",
    "23-24": "2023/24",
    "24-25": "2024/25",
    "25-26": "2025/26",
}

league_key = sys.argv[1] if len(sys.argv) > 1 else "laliga"
league_str, league_id = LEAGUES[league_key]
print(f"Scraping {league_str}...")

for sd_season, label in SEASONS.items():
    try:
        season = db.query(Season).filter(Season.label == label).first()
        if not season:
            print(f"  Season {label} not found, skipping")
            continue

        fbref = sd.FBref(leagues=league_str, seasons=sd_season)
        stats = fbref.read_player_season_stats(stat_type="standard")
        stats = stats.reset_index()
        print(f"  Got {len(stats)} rows for {sd_season}")

        saved = 0
        for _, row in stats.iterrows():
            try:
                player_name = str(row.get(("player", ""), "")).strip()
                if not player_name or player_name == "nan":
                    continue

                nationality = str(row.get(("nation", ""), "") or "")[:100]
                position = str(row.get(("pos", ""), "") or "")[:20]
                team_name = str(row.get(("team", ""), "") or "").strip()
                minutes = int(float(row.get(("Playing Time", "Min"), 0) or 0))
                goals = int(float(row.get(("Performance", "Gls"), 0) or 0))
                assists = int(float(row.get(("Performance", "Ast"), 0) or 0))

                player = db.query(Player).filter(Player.name == player_name).first()
                if not player:
                    player = Player(name=player_name, nationality=nationality or None, primary_position=position or None)
                    db.add(player)
                    db.flush()

                club = db.query(Club).filter(Club.name == team_name).first()
                if not club:
                    club = Club(name=team_name, country=league_str.split("-")[0])
                    db.add(club)
                    db.flush()

                existing = db.query(PlayerSeasonStats).filter(
                    PlayerSeasonStats.player_id == player.player_id,
                    PlayerSeasonStats.season_id == season.season_id,
                    PlayerSeasonStats.club_id == club.club_id
                ).first()

                if not existing:
                    pstat = PlayerSeasonStats(
                        player_id=player.player_id,
                        season_id=season.season_id,
                        club_id=club.club_id,
                        league_id=league_id,
                        minutes=minutes,
                        goals=goals,
                        assists=assists,
                        xG=0.0,
                        xA=0.0,
                    )
                    db.add(pstat)
                    saved += 1

            except Exception as e:
                continue

        db.commit()
        print(f"  Committed {saved} players for {sd_season}")
        print(f"  Waiting 60 seconds...")
        time.sleep(60)

    except Exception as e:
        db.rollback()
        print(f"  Failed {sd_season}: {e}")
        print(f"  Waiting 120 seconds...")
        time.sleep(120)

db.close()
print(f"Done with {league_str}!")




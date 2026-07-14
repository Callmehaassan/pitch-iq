import soccerdata as sd
from app.database import SessionLocal
from app.models.core import Club, TeamSeasonStats, Season
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
print(f"Scraping team stats for {league_str}...")

for sd_season, label in SEASONS.items():
    try:
        season = db.query(Season).filter(Season.label == label).first()
        if not season:
            print(f"  Season {label} not in DB, skipping")
            continue

        existing = db.query(TeamSeasonStats).filter(
            TeamSeasonStats.league_id == league_id,
            TeamSeasonStats.season_id == season.season_id,
            TeamSeasonStats.points != None,
            TeamSeasonStats.points > 0
        ).count()

        if existing >= 15:
            print(f"  {label} already has {existing} good rows, skipping")
            continue

        print(f"  Scraping {label}...")
        fbref = sd.FBref(leagues=league_str, seasons=sd_season)

        std = fbref.read_team_season_stats(stat_type="standard").reset_index()
        try:
            shoot = fbref.read_team_season_stats(stat_type="shooting").reset_index()
            has_shooting = True
        except:
            has_shooting = False
            print(f"  No shooting data for {label}")

        saved = 0
        for _, row in std.iterrows():
            try:
                team_name = str(row.get(("team", ""), "")).strip()
                if not team_name or team_name == "nan":
                    continue

                club = db.query(Club).filter(Club.name == team_name).first()
                if not club:
                    club = Club(name=team_name, country=league_str.split("-")[0])
                    db.add(club)
                    db.flush()

                mp = int(float(row.get(("Playing Time", "MP"), 0) or 0))
                gls = int(float(row.get(("Performance", "Gls"), 0) or 0))
                possession = float(row.get(("Poss", ""), 0) or 0)

                xg_val = 0.0
                xga_val = 0.0
                if has_shooting:
                    shoot_row = shoot[shoot[("team", "")] == team_name]
                    if not shoot_row.empty:
                        xg_val = float(shoot_row.iloc[0].get(("Expected", "xG"), 0) or 0)

                wins = gls // 3 if mp > 0 else 0
                pts = gls

                existing_stat = db.query(TeamSeasonStats).filter(
                    TeamSeasonStats.club_id == club.club_id,
                    TeamSeasonStats.league_id == league_id,
                    TeamSeasonStats.season_id == season.season_id
                ).first()

                if existing_stat:
                    existing_stat.matches_played = mp
                    existing_stat.possession = possession
                    existing_stat.xG = xg_val
                else:
                    stat = TeamSeasonStats(
                        club_id=club.club_id,
                        league_id=league_id,
                        season_id=season.season_id,
                        matches_played=mp,
                        possession=possession,
                        xG=xg_val,
                        xGA=xga_val,
                        points=0,
                        wins=0,
                        draws=0,
                        losses=0,
                    )
                    db.add(stat)
                saved += 1

            except Exception as e:
                continue

        db.commit()
        print(f"  Saved {saved} rows for {label}")

        try:
            schedule = fbref.read_schedule().reset_index()
            from collections import defaultdict
            team_pts = defaultdict(int)
            team_w = defaultdict(int)
            team_d = defaultdict(int)
            team_l = defaultdict(int)
            team_pos = {}

            for _, r in schedule.iterrows():
                home = str(r.get(("home_team", ""), "") or "")
                away = str(r.get(("away_team", ""), "") or "")
                hg = r.get(("home_goals", ""), None)
                ag = r.get(("away_goals", ""), None)
                if hg is None or ag is None or str(hg) == "nan":
                    continue
                hg, ag = int(float(hg)), int(float(ag))
                if hg > ag:
                    team_pts[home] += 3; team_w[home] += 1; team_l[away] += 1
                elif hg < ag:
                    team_pts[away] += 3; team_w[away] += 1; team_l[home] += 1
                else:
                    team_pts[home] += 1; team_pts[away] += 1
                    team_d[home] += 1; team_d[away] += 1

            sorted_teams = sorted(team_pts.keys(), key=lambda t: -team_pts[t])
            for pos, team in enumerate(sorted_teams, 1):
                team_pos[team] = pos

            for team, pts in team_pts.items():
                club = db.query(Club).filter(Club.name == team).first()
                if not club:
                    continue
                stat = db.query(TeamSeasonStats).filter(
                    TeamSeasonStats.club_id == club.club_id,
                    TeamSeasonStats.league_id == league_id,
                    TeamSeasonStats.season_id == season.season_id
                ).first()
                if stat:
                    stat.points = pts
                    stat.wins = team_w[team]
                    stat.draws = team_d[team]
                    stat.losses = team_l[team]
                    stat.position = team_pos.get(team, 0)

            db.commit()
            print(f"  Updated points/positions from schedule")
        except Exception as e:
            print(f"  Could not get schedule: {e}")

        print(f"  Waiting 60s...")
        time.sleep(60)

    except Exception as e:
        db.rollback()
        print(f"  Failed {label}: {e}")
        time.sleep(120)

db.close()
print(f"Done with {league_str}!")

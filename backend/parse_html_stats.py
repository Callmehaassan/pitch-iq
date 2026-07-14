
import os
import re
from bs4 import BeautifulSoup
from app.database import SessionLocal
from app.models.core import Club, TeamSeasonStats, Season
from datetime import date

MANUAL_DIR = "D:/Anamssii/pitch-iq/soccerdata_cache/manual_downloads"

LEAGUE_MAP = {
    "epl": ("ENG-Premier League", 1),
    "laliga": ("ESP-La Liga", 2),
    "bundesliga": ("GER-Bundesliga", 3),
    "seriea": ("ITA-Serie A", 4),
    "ligue1": ("FRA-Ligue 1", 5),
}

SEASON_MAP = {
    "2020-21": "2020/21",
    "2021-22": "2021/22",
    "2022-23": "2022/23",
    "2023-24": "2023/24",
    "2024-25": "2024/25",
    "2025-26": "2025/26",
}

def get_cell_text(row, stat):
    cell = row.find(["td", "th"], {"data-stat": stat})
    if cell:
        return cell.text.strip()
    return ""

def get_team_name(row):
    cell = row.find("td", {"data-stat": "team"})
    if not cell:
        return ""
    a = cell.find("a")
    if a:
        return a.text.strip()
    return cell.text.strip()

def parse_html_file(filepath, league_key, season_str):
    league_name, league_id = LEAGUE_MAP[league_key]
    season_label = SEASON_MAP.get(season_str)
    if not season_label:
        print(f"  Unknown season: {season_str}")
        return 0

    db = SessionLocal()
    try:
        season = db.query(Season).filter(Season.label == season_label).first()
        if not season:
            year = int(season_str[:4])
            season = Season(
                label=season_label,
                start_date=date(year, 8, 1),
                end_date=date(year + 1, 5, 31)
            )
            db.add(season)
            db.flush()
            print(f"  Created season {season_label}")

        with open(filepath, encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")

        standings_table = None
        for t in soup.find_all("table"):
            tid = t.get("id", "")
            if "overall" in tid and "results" in tid:
                standings_table = t
                break

        if not standings_table:
            print(f"  No standings table found")
            return 0

        xg_map = {}
        for t in soup.find_all("table"):
            tid = t.get("id", "")
            if "shooting_for" in tid:
                for row in t.find_all("tr"):
                    team = get_team_name(row)
                    xg_text = get_cell_text(row, "xg")
                    if team and xg_text:
                        try:
                            xg_map[team] = float(xg_text)
                        except:
                            pass
                break

        saved = 0
        for row in standings_table.find_all("tr"):
            rk_cell = row.find(["td", "th"], {"data-stat": "rank"})
            if not rk_cell:
                continue
            try:
                rank = int(rk_cell.text.strip())
            except:
                continue

            team_name = get_team_name(row)
            if not team_name:
                continue

            mp = int(get_cell_text(row, "games") or 0)
            w = int(get_cell_text(row, "wins") or 0)
            d = int(get_cell_text(row, "ties") or 0)
            l = int(get_cell_text(row, "losses") or 0)
            pts_text = get_cell_text(row, "points")
            pts = int(pts_text) if pts_text else (w * 3 + d)
            gf_text = get_cell_text(row, "goals_for")
            ga_text = get_cell_text(row, "goals_against")
            gf = int(gf_text) if gf_text else 0
            ga = int(ga_text) if ga_text else 0
            xg = xg_map.get(team_name, 0.0)

            club = db.query(Club).filter(Club.name == team_name).first()
            if not club:
                club = Club(name=team_name, country=league_name.split("-")[0])
                db.add(club)
                db.flush()

            existing = db.query(TeamSeasonStats).filter(
                TeamSeasonStats.club_id == club.club_id,
                TeamSeasonStats.league_id == league_id,
                TeamSeasonStats.season_id == season.season_id
            ).first()

            if existing:
                existing.points = pts
                existing.wins = w
                existing.draws = d
                existing.losses = l
                existing.matches_played = mp
                existing.position = rank
                existing.xG = xg
                existing.xGA = float(ga)
            else:
                stat = TeamSeasonStats(
                    club_id=club.club_id,
                    league_id=league_id,
                    season_id=season.season_id,
                    points=pts,
                    wins=w,
                    draws=d,
                    losses=l,
                    matches_played=mp,
                    position=rank,
                    xG=xg,
                    xGA=float(ga),
                    possession=0.0,
                )
                db.add(stat)
            saved += 1

        db.commit()
        return saved

    except Exception as e:
        db.rollback()
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        db.close()


def run():
    files = [f for f in os.listdir(MANUAL_DIR) if f.endswith(".html")]
    print(f"Found {len(files)} HTML files")

    total = 0
    for fname in sorted(files):
        match = re.match(r"^([a-z1]+)_(\d{4}-\d{2})\.html$", fname)
        if not match:
            continue
        league_key = match.group(1)
        season_str = match.group(2)

        if league_key not in LEAGUE_MAP:
            continue

        filepath = os.path.join(MANUAL_DIR, fname)
        print(f"Parsing {fname}...")
        saved = parse_html_file(filepath, league_key, season_str)
        print(f"  Saved/updated {saved} rows")
        total += saved

    print(f"Total rows saved: {total}")

if __name__ == "__main__":
    run()

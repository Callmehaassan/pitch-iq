from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.core import Player, PlayerSeasonStats, TeamSeasonStats, Club, Season

SEASON_LABELS = {1: '2024/25', 2: '2023/24', 3: '2022/23', 4: '2020/21', 5: '2021/22', 6: '2025/26'}
LEAGUE_NAMES  = {1: 'Premier League', 2: 'La Liga', 3: 'Bundesliga', 4: 'Serie A', 5: 'Ligue 1'}

def search_players(db: Session, name=None, position=None, league_id=None, season_id=None, min_goals=None, limit=20):
    q = db.query(Player, PlayerSeasonStats, Club, Season).join(
        PlayerSeasonStats, Player.player_id == PlayerSeasonStats.player_id
    ).join(Club, PlayerSeasonStats.club_id == Club.club_id
    ).join(Season, PlayerSeasonStats.season_id == Season.season_id)
    if name:
        q = q.filter(Player.name.ilike(f"%{name}%"))
    if position:
        q = q.filter(Player.primary_position.ilike(f"%{position}%"))
    if league_id:
        q = q.filter(PlayerSeasonStats.league_id == league_id)
    if season_id:
        q = q.filter(PlayerSeasonStats.season_id == season_id)
    if min_goals is not None:
        q = q.filter(PlayerSeasonStats.goals >= min_goals)
    rows = q.order_by(desc(PlayerSeasonStats.goals)).limit(limit).all()
    return [{
        "player_id": p.player_id, "name": p.name, "nationality": p.nationality,
        "position": p.primary_position, "club": c.name, "season": s.label,
        "league": LEAGUE_NAMES.get(st.league_id, ""), "goals": st.goals or 0,
        "assists": st.assists or 0, "minutes": st.minutes or 0,
        "xG": round(st.xG or 0, 2), "xA": round(st.xA or 0, 2),
    } for p, st, c, s in rows]

def get_top_scorers(db: Session, league_id=None, season_id=None, limit=20):
    return search_players(db, league_id=league_id, season_id=season_id, limit=limit)

def get_player_career(db: Session, player_id: int):
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        return None
    rows = db.query(PlayerSeasonStats, Club, Season).join(
        Club, PlayerSeasonStats.club_id == Club.club_id
    ).join(Season, PlayerSeasonStats.season_id == Season.season_id
    ).filter(PlayerSeasonStats.player_id == player_id
    ).order_by(Season.label).all()
    seasons = [{
        "season": s.label, "club": c.name, "league": LEAGUE_NAMES.get(st.league_id, ""),
        "goals": st.goals or 0, "assists": st.assists or 0, "minutes": st.minutes or 0,
        "xG": round(st.xG or 0, 2), "xA": round(st.xA or 0, 2),
    } for st, c, s in rows]
    return {
        "player_id": player.player_id, "name": player.name,
        "nationality": player.nationality, "position": player.primary_position,
        "seasons": seasons,
        "total_goals": sum(s["goals"] for s in seasons),
        "total_assists": sum(s["assists"] for s in seasons),
        "total_minutes": sum(s["minutes"] for s in seasons),
    }

def get_player_career_by_name(db: Session, name: str):
    players = db.query(Player).filter(Player.name.ilike(f"%{name}%")).all()
    if not players:
        return []
    careers = []
    for p in players:
        career = get_player_career(db, p.player_id)
        if career:
            careers.append(career)
    return careers

def get_team_stats(db: Session, club_name=None, league_id=None):
    q = db.query(TeamSeasonStats, Club, Season).join(
        Club, TeamSeasonStats.club_id == Club.club_id
    ).join(Season, TeamSeasonStats.season_id == Season.season_id)
    if club_name:
        q = q.filter(Club.name.ilike(f"%{club_name}%"))
    if league_id:
        q = q.filter(TeamSeasonStats.league_id == league_id)
    rows = q.order_by(Season.label).all()
    return [{
        "club": c.name, "season": s.label, "league": LEAGUE_NAMES.get(st.league_id, ""),
        "points": st.points, "position": st.position,
        "xG": round(st.xG or 0, 2), "xGA": round(st.xGA or 0, 2),
        "wins": st.wins, "draws": st.draws, "losses": st.losses,
        "possession": st.possession,
    } for st, c, s in rows]

def get_team_stats_by_name(db: Session, club_name: str):
    clubs = db.query(Club).filter(Club.name.ilike(f"%{club_name}%")).all()
    if not clubs:
        return []
    all_stats = []
    for c in clubs:
        stats = get_team_stats(db, club_name=c.name)
        all_stats.extend(stats)
    return all_stats

def compute_transfer_impact(db: Session, player_id: int, from_club_id: int, to_club_id: int):
    player = db.query(Player).filter(Player.player_id == player_id).first()
    latest = db.query(PlayerSeasonStats).filter(
        PlayerSeasonStats.player_id == player_id
    ).order_by(desc(PlayerSeasonStats.season_id)).first()
    from_club = db.query(Club).filter(Club.club_id == from_club_id).first()
    to_club   = db.query(Club).filter(Club.club_id == to_club_id).first()
    from_team = db.query(TeamSeasonStats).filter(
        TeamSeasonStats.club_id == from_club_id
    ).order_by(desc(TeamSeasonStats.season_id)).first()
    to_team = db.query(TeamSeasonStats).filter(
        TeamSeasonStats.club_id == to_club_id
    ).order_by(desc(TeamSeasonStats.season_id)).first()
    goals = latest.goals or 0 if latest else 0
    assists = latest.assists or 0 if latest else 0
    xg = latest.xG or 0 if latest else 0
    xa = latest.xA or 0 if latest else 0
    minutes = latest.minutes or 0 if latest else 0
    goal_contrib_pts = (goals * 1.8) + (assists * 0.9)
    from_pts_delta = round(-goal_contrib_pts * 0.7, 1)
    to_pts_delta   = round(goal_contrib_pts * 0.85, 1)
    from_xg_delta  = round(-xg * 0.65, 2)
    to_xg_delta    = round(xg * 0.80, 2)
    from_pts = from_team.points if from_team else 50
    to_pts   = to_team.points   if to_team   else 50
    from_ucl_delta = round(max(-0.25, from_pts_delta / max(from_pts, 1) * -0.3), 3)
    to_ucl_delta   = round(min(0.30,  to_pts_delta   / max(to_pts,   1) *  0.3), 3)
    return {
        "player_name": player.name if player else f"Player {player_id}",
        "position": player.primary_position if player else "",
        "last_season_goals": goals, "last_season_assists": assists,
        "last_season_xG": round(xg, 2), "last_season_xA": round(xa, 2),
        "last_season_minutes": minutes,
        "from_club": from_club.name if from_club else f"Club {from_club_id}",
        "to_club":   to_club.name   if to_club   else f"Club {to_club_id}",
        "from_club_points_delta": from_pts_delta,
        "to_club_points_delta":   to_pts_delta,
        "from_club_xG_delta":     from_xg_delta,
        "to_club_xG_delta":       to_xg_delta,
        "from_club_ucl_prob_delta": from_ucl_delta,
        "to_club_ucl_prob_delta":   to_ucl_delta,
        "from_club_last_points":  from_pts,
        "to_club_last_points":    to_pts,
    }

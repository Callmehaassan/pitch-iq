from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from groq import Groq
from app.config import settings
from app.database import get_db
from app.schemas.agent import AgentQueryRequest, AgentQueryResponse
from app.agents.scout_service import (
    search_players, get_top_scorers, get_team_stats,
    get_player_career_by_name, get_team_stats_by_name
)
from app.models.core import Club
import uuid
import re

router = APIRouter(prefix="/agent", tags=["Agents"])
client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
session_histories = {}

LEAGUE_MAP = {
    "premier league": 1, "epl": 1, "english premier league": 1, "premierleague": 1,
    "la liga": 2, "laliga": 2, "spanish la liga": 2,
    "bundesliga": 3, "german bundesliga": 3,
    "serie a": 4, "seriea": 4, "italian serie a": 4,
    "ligue 1": 5, "ligue1": 5, "french ligue 1": 5
}

SEASON_MAP = {
    "2020/21": 4, "2020-21": 4, "2020_21": 4, "20/21": 4, "2020": 4,
    "2021/22": 5, "2021-22": 5, "2021_22": 5, "21/22": 5, "2021": 5,
    "2022/23": 3, "2022-23": 3, "2022_23": 3, "22/23": 3, "2022": 3,
    "2023/24": 2, "2023-24": 2, "2023_24": 2, "23/24": 2, "2023": 2,
    "2024/25": 1, "2024-25": 1, "2024_25": 1, "24/25": 1, "2024": 1,
    "2025/26": 6, "2025-26": 6, "2025_26": 6, "25/26": 6, "2025": 6, "2026": 6
}

POS_MAP = {"striker": "FW", "forward": "FW", "winger": "FW", "midfielder": "MF", "defender": "DF", "goalkeeper": "GK"}

TEAM_KEYWORDS    = ["team stats", "club stats", "standing", "points table", "possession", "best team", "strongest team"]
SCORER_KEYWORDS  = ["top scorer", "most goals", "golden boot", "best striker", "who scored most"]
PLAYER_KEYWORDS  = ["player", "find", "search", "stats", "goals", "assists", "xg", "minutes",
                    "midfielder", "defender", "forward", "goalkeeper", "striker", "winger",
                    "market value", "value", "career", "history", "season", "performance",
                    "who is", "show me", "tell me", "how many", "what did", "played for"]

SKIP_WORDS = {
    "what", "is", "the", "of", "who", "are", "show", "me", "find", "best", "top", "in", "a", "an",
    "for", "with", "how", "many", "goals", "assists", "stats", "current", "market", "value",
    "did", "tell", "their", "his", "her", "this", "that", "season", "league", "club", "team",
    "player", "transfer", "played", "performance", "career", "history", "last", "all",
    "epl", "laliga", "bundesliga", "seriea", "ligue1", "premier", "liga", "serie", "ligue",
    "2020", "2021", "2022", "2023", "2024", "2025", "2026", "groq", "llm", "pitch", "iq", "scout", "ai",
    "compare", "vs", "against", "or", "and", "between", "he", "she", "they", "it"
}

def extract_league(t):
    for k, v in LEAGUE_MAP.items():
        if k in t: return v
    return None

def extract_season(t):
    for k, v in SEASON_MAP.items():
        if k in t: return v
    return None

def extract_position(t):
    for k, v in POS_MAP.items():
        if k in t: return v
    return None

def get_query_proper_nouns(query: str):
    words = re.findall(r'\b[A-Z][a-zA-Z]*\b', query)
    candidates = []
    for w in words:
        wl = w.lower()
        if wl not in SKIP_WORDS:
            candidates.append(w)
    return candidates

def extract_search_terms(query: str):
    proper_nouns = get_query_proper_nouns(query)
    if proper_nouns:
        return proper_nouns
    
    words = re.findall(r'\b[a-zA-Z]{3,}\b', query)
    candidates = []
    for w in words:
        wl = w.lower()
        if wl not in SKIP_WORDS:
            candidates.append(w)
    return candidates

def fmt_career_table(career):
    if not career:
        return "not found in Pitch IQ database"
    lines = []
    lines.append(f"PLAYER: {career['name']} ({career['nationality'] or 'N/A'}) - {career['position'] or 'N/A'}")
    lines.append(f"Seasons Found: {', '.join(s['season'] for s in career['seasons'])}")
    lines.append(f"Career Totals: Goals: {career['total_goals']} | Assists: {career['total_assists']} | Minutes: {career['total_minutes']}")
    lines.append("")
    lines.append("Season Breakdown:")
    lines.append("Season | Club | League | Goals | Assists | Minutes | xG | xA")
    lines.append("-" * 75)
    for s in career['seasons']:
        lines.append(f"{s['season']} | {s['club']} | {s['league']} | {s['goals']} | {s['assists']} | {s['minutes']} | {s['xG']} | {s['xA']}")
    return "\n".join(lines)

def fmt_team_stats_table(stats):
    if not stats:
        return "No team stats found."
    club_name = stats[0]['club']
    lines = []
    lines.append(f"TEAM HISTORY: {club_name}")
    lines.append("Season | League | Position | Points | Wins | Draws | Losses | xG | xGA | Possession")
    lines.append("-" * 90)
    for r in stats:
        lines.append(f"{r['season']} | {r['league']} | {r['position']} | {r['points']} | {r['wins']} | {r['draws']} | {r['losses']} | {r['xG']} | {r['xGA']} | {r['possession']}")
    return "\n".join(lines)

def fmt_comparison(career1, career2):
    lines = []
    lines.append(f"=== PLAYER COMPARISON: {career1['name']} vs {career2['name']} ===")
    lines.append(f"Nationality: {career1['nationality']} vs {career2['nationality']}")
    lines.append(f"Position: {career1['position']} vs {career2['position']}")
    lines.append(f"Career Goals: {career1['total_goals']} vs {career2['total_goals']}")
    lines.append(f"Career Assists: {career1['total_assists']} vs {career2['total_assists']}")
    lines.append(f"Career Minutes: {career1['total_minutes']} vs {career2['total_minutes']}")
    lines.append("")
    lines.append("Season by Season Breakdown:")
    
    s1 = {s['season']: s for s in career1['seasons']}
    s2 = {s['season']: s for s in career2['seasons']}
    all_seasons = sorted(list(set(s1.keys()) | set(s2.keys())))
    
    lines.append("Season | Club (P1) | G/A (P1) | Club (P2) | G/A (P2)")
    lines.append("-" * 65)
    for s in all_seasons:
        p1_stat = s1.get(s, {"club": "N/A", "goals": 0, "assists": 0})
        p2_stat = s2.get(s, {"club": "N/A", "goals": 0, "assists": 0})
        lines.append(f"{s} | {p1_stat['club']} | {p1_stat['goals']}G/{p1_stat['assists']}A | {p2_stat['club']} | {p2_stat['goals']}G/{p2_stat['assists']}A")
    return "\n".join(lines)

def fmt_top_scorers_table(rows):
    if not rows:
        return "No top scorers found."
    lines = []
    lines.append("Top Scorers:")
    lines.append("Player | Team | League | Season | Goals | Assists | Minutes")
    lines.append("-" * 75)
    for r in rows:
        lines.append(f"{r['name']} | {r['club']} | {r['league']} | {r['season']} | {r['goals']} | {r['assists']} | {r['minutes']}")
    return "\n".join(lines)

def query_db(query: str, db: Session):
    q = query.lower()
    league_id = extract_league(q)
    season_id = extract_season(q)
    position  = extract_position(q)
    
    # 1. Check for comparison mode
    if any(w in q for w in ["compare", " vs ", " vs. ", "versus"]):
        terms = extract_search_terms(query)
        if len(terms) >= 2:
            careers1 = get_player_career_by_name(db, terms[0])
            careers2 = get_player_career_by_name(db, terms[1])
            if careers1 and careers2:
                return fmt_comparison(careers1[0], careers2[0])
            elif careers1:
                return f"Only one player found.\n" + fmt_career_table(careers1[0])
            elif careers2:
                return f"Only one player found.\n" + fmt_career_table(careers2[0])
            else:
                return f"Players '{terms[0]}' and '{terms[1]}' not found in Pitch IQ database."
    
    # 2. Check for top scorers mode
    if any(w in q for w in SCORER_KEYWORDS):
        rows = get_top_scorers(db, league_id=league_id, season_id=season_id, limit=20)
        return fmt_top_scorers_table(rows)
    
    # Extract candidate terms for name searches
    terms = extract_search_terms(query)
    
    # 3. Check for team stats mode (if any term matches a club name in the DB)
    for term in terms:
        club = db.query(Club).filter(Club.name.ilike(f"%{term}%")).first()
        if club:
            stats = get_team_stats_by_name(db, club.name)
            if stats:
                return fmt_team_stats_table(stats)
    
    # 4. Check for player stats mode (if any term matches a player in the DB)
    player_careers = []
    for term in terms:
        careers = get_player_career_by_name(db, term)
        if careers:
            player_careers.extend(careers)
    
    if player_careers:
        return "\n\n".join(fmt_career_table(c) for c in player_careers)
    
    # 5. Position or general player keyword queries
    if position or any(w in q for w in PLAYER_KEYWORDS):
        rows = search_players(db, position=position, league_id=league_id, season_id=season_id, limit=20)
        return fmt_top_scorers_table(rows)
        
    # 6. Fallback: search for top players filtered by league/season
    rows = search_players(db, league_id=league_id, season_id=season_id, limit=10)
    if rows:
        return fmt_top_scorers_table(rows)
    
    return "not found in Pitch IQ database"

@router.post("/ask", response_model=AgentQueryResponse)
def ask_data(request: AgentQueryRequest, db: Session = Depends(get_db)):
    session_id = request.session_id or str(uuid.uuid4())
    db_context = query_db(request.query, db)
    history = session_histories.get(session_id, [])
    history.append({"role": "user", "content": request.query})
    if len(history) > 8:
        history = history[-8:]
    
    if not client:
        return AgentQueryResponse(response=db_context, session_id=session_id, groq_available=False)
    
    try:
        system = """You are Pitch IQ Scout AI with access to real football data from 2020/21 to 2025/26.
IMPORTANT RULES:
- You ONLY use the database results provided below.
- Never use your own training knowledge for any stats, numbers, goals, assists, or market values.
- If a player is not in the database results, you MUST explicitly say: "not found in Pitch IQ database".
- Your response should ALWAYS include:
  1. Which seasons were found
  2. Career totals (total goals, assists, minutes)
  3. A detailed season-by-season breakdown
- Do not summarize, truncate, or skip any seasons or rows present in the database results.
- Always mention the season and club when giving stats.
- Be specific with numbers, mentioning the season and club for each row."""
        system += f"\n\nLIVE DATABASE RESULTS:\n{db_context}"
        messages = [{"role": "system", "content": system}] + history
        resp = client.chat.completions.create(
            model=settings.GROQ_AGENT_MODEL,
            messages=messages, temperature=0.1, max_tokens=600
        )
        reply = resp.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        session_histories[session_id] = history
        return AgentQueryResponse(response=reply, session_id=session_id, groq_available=True)
    except Exception:
        return AgentQueryResponse(response=db_context, session_id=session_id, groq_available=False)

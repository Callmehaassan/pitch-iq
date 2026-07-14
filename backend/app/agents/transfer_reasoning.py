from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from groq import Groq
from app.config import settings
from app.database import get_db
from app.schemas.agent import TransferSimRequest, TransferSimResponse
from app.agents.scout_service import compute_transfer_impact

router = APIRouter(prefix="/agent", tags=["Agents"])
client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

@router.post("/transfer-reasoning", response_model=TransferSimResponse)
def transfer_reasoning(request: TransferSimRequest, db: Session = Depends(get_db)):
    impact = compute_transfer_impact(db, request.player_id, request.from_club_id, request.to_club_id)
    narrative = None
    groq_ok = False
    if client:
        try:
            prompt = f"""Transfer analysis (Pitch IQ data 2020-26):
Player: {impact['player_name']} ({impact['position']})
Last season: {impact['last_season_goals']}G {impact['last_season_assists']}A {impact['last_season_xG']}xG {impact['last_season_minutes']}mins
FROM {impact['from_club']} ({impact['from_club_last_points']}pts) -> {impact['from_club_points_delta']:+}pts {impact['from_club_xG_delta']:+}xG
TO   {impact['to_club']}   ({impact['to_club_last_points']}pts) -> {impact['to_club_points_delta']:+}pts {impact['to_club_xG_delta']:+}xG
Write a 120-word analyst summary. Be specific about goal contribution, attacking threat, and league position impact."""
            resp = client.chat.completions.create(model=settings.GROQ_AGENT_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.4, max_tokens=250)
            narrative = resp.choices[0].message.content
            groq_ok = True
        except Exception:
            pass
    return TransferSimResponse(
        player_name=impact["player_name"], from_club=impact["from_club"], to_club=impact["to_club"],
        from_club_points_delta=impact["from_club_points_delta"], to_club_points_delta=impact["to_club_points_delta"],
        from_club_ucl_prob_delta=impact["from_club_ucl_prob_delta"], to_club_ucl_prob_delta=impact["to_club_ucl_prob_delta"],
        narrative=narrative, groq_available=groq_ok
    )

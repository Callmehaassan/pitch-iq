from fastapi import APIRouter, HTTPException
from groq import Groq
from app.config import settings
from app.utils.groq_rate_limiter import agent_limiter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/agent", tags=["Agents"])
client = Groq(api_key=settings.GROQ_API_KEY)

class AnalystBriefResponse(BaseModel):
    fixture_id: int
    brief: str
    groq_available: bool = True

@router.get("/analyst/brief/{fixture_id}", response_model=AnalystBriefResponse)
def get_analyst_brief(fixture_id: int):
    if not agent_limiter.can_request(estimated_tokens=300):
        return AnalystBriefResponse(
            fixture_id=fixture_id,
            brief="AI narrative unavailable due to rate limiting.",
            groq_available=False
        )
    
    if not settings.GROQ_API_KEY:
        return AnalystBriefResponse(
            fixture_id=fixture_id,
            brief="Groq API key not configured.",
            groq_available=False
        )

    try:
        agent_limiter.consume(300)
        response = client.chat.completions.create(
            model=settings.GROQ_AGENT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a 120-180 word match preview brief for fixture {fixture_id}. Cover predicted outcome, key reasons, and risk factors."
                }
            ],
            temperature=0.4,
            max_tokens=300
        )
        brief = response.choices[0].message.content
        return AnalystBriefResponse(fixture_id=fixture_id, brief=brief, groq_available=True)
    except Exception as e:
        return AnalystBriefResponse(
            fixture_id=fixture_id,
            brief="AI narrative temporarily unavailable.",
            groq_available=False
        )

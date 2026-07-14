from pydantic import BaseModel
from typing import Optional

class AgentQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class AgentQueryResponse(BaseModel):
    response: str
    session_id: str
    groq_available: bool = True

class TransferSimRequest(BaseModel):
    player_id: int
    from_club_id: int
    to_club_id: int

class TransferSimResponse(BaseModel):
    player_name: str
    from_club: str
    to_club: str
    from_club_points_delta: float
    to_club_points_delta: float
    from_club_ucl_prob_delta: float
    to_club_ucl_prob_delta: float
    narrative: Optional[str] = None
    groq_available: bool = True

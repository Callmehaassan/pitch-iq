from fastapi import APIRouter
from groq import Groq
from tavily import TavilyClient
from app.config import settings
from app.schemas.agent import AgentQueryRequest, AgentQueryResponse
import uuid

router = APIRouter(prefix="/agent", tags=["Agents"])
client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
session_histories = {}

def search_web(query: str) -> str:
    try:
        tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = tavily.search(query=query, max_results=4, search_depth="basic")
        snippets = []
        for r in results.get("results", []):
            snippets.append(r.get("content", "")[:400])
        return "\n".join(snippets) if snippets else ""
    except Exception:
        return ""

@router.post("/transfer", response_model=AgentQueryResponse)
def transfer_analysis(request: AgentQueryRequest):
    session_id = request.session_id or str(uuid.uuid4())

    if not client:
        return AgentQueryResponse(
            response="Groq API not configured.",
            session_id=session_id,
            groq_available=False
        )

    web_context = search_web(f"football transfer {request.query} stats impact 2024 2025")

    system = """You are Pitch IQ Transfer Simulator. You have data from 2020/21 to 2025/26 covering EPL, La Liga, Bundesliga, Serie A and Ligue 1. When given a hypothetical transfer scenario:
1. Analyze the SELLING club: predicted points lost, UCL probability change, key stats lost
2. Analyze the BUYING club: predicted points gained, UCL probability change, key stats gained
3. Give specific numbers based on the player's actual stats
4. Use web search data if available, otherwise use your football knowledge
5. ALWAYS provide a full analysis - never say a player is not found
Format: clear sections for each club with bullet points and specific numbers."""

    if web_context:
        system += f"\n\nWeb search results:\n{web_context}"

    history = session_histories.get(session_id, [])
    history.append({"role": "user", "content": request.query})
    if len(history) > 6:
        history = history[-6:]

    try:
        messages = [{"role": "system", "content": system}] + history
        resp = client.chat.completions.create(
            model=settings.GROQ_AGENT_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=700
        )
        reply = resp.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        session_histories[session_id] = history
        return AgentQueryResponse(response=reply, session_id=session_id, groq_available=True)
    except Exception as e:
        return AgentQueryResponse(
            response="Transfer analysis temporarily unavailable. Please try again.",
            session_id=session_id,
            groq_available=False
        )

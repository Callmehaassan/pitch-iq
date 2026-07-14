from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
import app.models.core
import app.models.user
from app.api import leagues, players, predictions
from app.api.routes_ucl import router as ucl_router
from app.auth import router as auth_router
from app.agents import analyst, ask_data, transfer_reasoning, transfer_agent

app = FastAPI(
    title="Pitch IQ API",
    description="Multi-League Football Performance Prediction System",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(leagues.router)
app.include_router(predictions.router)
app.include_router(players.router)
app.include_router(auth_router.router)
app.include_router(analyst.router)
app.include_router(ask_data.router)
app.include_router(transfer_reasoning.router)
app.include_router(transfer_agent.router)
app.include_router(ucl_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Pitch IQ API is running"}

def health():
    return {"status": "healthy"}

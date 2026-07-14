from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./pitchiq.db"
    
    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_AGENT_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_SENTIMENT_MODEL: str = "llama-3.1-8b-instant"
    
    # Tavily
    TAVILY_API_KEY: str = ""
    
    # Reddit
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "PitchIQ/1.0"
    
    # NewsAPI
    NEWS_API_KEY: str = ""
    
    # Auth
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()

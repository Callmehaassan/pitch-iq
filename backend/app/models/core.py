from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text, SmallInteger, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base

class League(Base):
    __tablename__ = "leagues"
    league_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    tier = Column(Integer, nullable=False, default=1)

class Season(Base):
    __tablename__ = "seasons"
    season_id = Column(Integer, primary_key=True, index=True)
    label = Column(String(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

class Club(Base):
    __tablename__ = "clubs"
    club_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)

class Player(Base):
    __tablename__ = "players"
    player_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    nationality = Column(String(100), nullable=True)
    primary_position = Column(String(20), nullable=True)

class TeamSeasonStats(Base):
    __tablename__ = "team_season_stats"
    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.club_id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.league_id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.season_id"), nullable=False)
    points = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    xG = Column(Float, nullable=True)
    xGA = Column(Float, nullable=True)
    possession = Column(Float, nullable=True)
    squad_value = Column(Float, nullable=True)
    matches_played = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=True)
    draws = Column(Integer, nullable=True)
    losses = Column(Integer, nullable=True)

class PlayerSeasonStats(Base):
    __tablename__ = "player_season_stats"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.season_id"), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.club_id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.league_id"), nullable=False)
    minutes = Column(Integer, nullable=True)
    goals = Column(Integer, nullable=True)
    assists = Column(Integer, nullable=True)
    xG = Column(Float, nullable=True)
    xA = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)

class Transfer(Base):
    __tablename__ = "transfers"
    transfer_id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False)
    from_club_id = Column(Integer, ForeignKey("clubs.club_id"), nullable=True)
    to_club_id = Column(Integer, ForeignKey("clubs.club_id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.season_id"), nullable=False)
    window = Column(String(10), nullable=False)

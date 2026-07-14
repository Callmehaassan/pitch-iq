from app.models.core import Club
from sqlalchemy.orm import Session

def search_clubs_by_name(name: str, db: Session, limit: int = 8):
    q = db.query(Club)
    if name:
        q = q.filter(Club.name.ilike(f"%{name}%"))
    return q.limit(limit).all()

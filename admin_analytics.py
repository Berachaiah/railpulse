from sqlalchemy import func
from sqlalchemy.orm import Session
from models import UserPreference, User

def top_routes(db: Session, limit: int = 10):
    rows = (
        db.query(UserPreference.route, func.count(UserPreference.id).label("count"))
        .group_by(UserPreference.route)
        .order_by(func.count(UserPreference.id).desc())
        .limit(limit)
        .all()
    )
    return [{"route": r.route, "count": r.count} for r in rows]

def top_stations(db: Session, limit: int = 10):
    rows = (
        db.query(UserPreference.station, func.count(UserPreference.id).label("count"))
        .group_by(UserPreference.station)
        .order_by(func.count(UserPreference.id).desc())
        .limit(limit)
        .all()
    )
    return [{"station": r.station, "count": r.count} for r in rows]

def total_users(db: Session) -> int:
    return db.query(User).count()

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.serializers import event_to_dict
from app.database.db_connection import get_db
from app.database.models import Event

router = APIRouter(prefix='/events', tags=['events'])


@router.get('/latest')
def latest_events(limit: int = 100, db: Session = Depends(get_db)):
    rows = db.scalars(select(Event).order_by(desc(Event.timestamp)).limit(limit)).all()
    return [event_to_dict(row) for row in rows]


@router.get('/high-impact')
def high_impact_events(threshold: float = 70, db: Session = Depends(get_db)):
    rows = db.scalars(select(Event).where(Event.impact_score >= threshold).order_by(desc(Event.timestamp)).limit(200)).all()
    return [event_to_dict(row) for row in rows]


@router.get('/company/{ticker}')
def company_events(ticker: str, db: Session = Depends(get_db)):
    rows = db.scalars(select(Event).where(Event.ticker == ticker.upper()).order_by(desc(Event.timestamp)).limit(200)).all()
    return [event_to_dict(row) for row in rows]


@router.get('/sector/{sector}')
def sector_events(sector: str, db: Session = Depends(get_db)):
    rows = db.scalars(select(Event).where(Event.sector.ilike(sector)).order_by(desc(Event.timestamp)).limit(200)).all()
    return [event_to_dict(row) for row in rows]


@router.get('/rumor-signals')
def rumor_signals(db: Session = Depends(get_db)):
    rows = db.scalars(select(Event).where(Event.rumor_probability.is_not(None)).order_by(desc(Event.rumor_probability)).limit(100)).all()
    return [event_to_dict(row) for row in rows]


@router.get('/pre-earnings')
def pre_earnings(db: Session = Depends(get_db)):
    rows = db.scalars(select(Event).where(Event.event_type == 'earnings').order_by(desc(Event.impact_score)).limit(100)).all()
    return [event_to_dict(row) for row in rows]

from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Float, Text, Date, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db_connection import Base


class Security(Base):
    __tablename__ = 'securities'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(32), index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    exchange: Mapped[str] = mapped_column(String(16), nullable=False)
    sector: Mapped[str] = mapped_column(String(128), default='Unknown')
    industry: Mapped[str] = mapped_column(String(128), default='Unknown')
    instrument_type: Mapped[str] = mapped_column(String(64), nullable=False)
    listing_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    ticker: Mapped[str] = mapped_column(String(32), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    source: Mapped[str] = mapped_column(String(100), index=True)
    sentiment: Mapped[str] = mapped_column(String(32), index=True)
    impact_score: Mapped[float] = mapped_column(Float)
    confidence_score: Mapped[float] = mapped_column(Float)
    sector: Mapped[str] = mapped_column(String(128), index=True)
    description: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(1000))
    dedupe_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    rumor_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


Index('idx_event_lookup', Event.timestamp, Event.ticker, Event.event_type)

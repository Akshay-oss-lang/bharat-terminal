from datetime import datetime

from celery import Celery
from sqlalchemy import select

from app.collectors.news_scraper import NewsScraper
from app.collectors.filings_scraper import run_filings_scraper
from app.collectors.regulatory_scraper import RegulatoryScraper
from app.collectors.social_scraper import SocialScraper
from app.config import get_settings
from app.database.db_connection import SessionLocal
from app.database.models import Event
from app.database.search_index import EventSearchIndex
from app.processors.rumor_detector import RumorDetector
from app.processors.sentiment_engine import SentimentEngine
from app.security_master.master_updater import SecurityMasterUpdater
from app.streaming.event_consumer import EventConsumer

settings = get_settings()
celery_app = Celery('bharat_intelligence', broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.timezone = 'Asia/Kolkata'


@celery_app.task
def scrape_news() -> int:
    return NewsScraper().run()



@celery_app.task
def scrape_filings() -> int:
    run_filings_scraper()
    return 1

@celery_app.task
def scrape_regulatory() -> int:
    return RegulatoryScraper().run()


@celery_app.task
def scrape_social() -> int:
    return SocialScraper().run()


@celery_app.task
def update_security_master() -> int:
    with SessionLocal() as db:
        return SecurityMasterUpdater().run(db)


@celery_app.task
def process_stream(consumer_name: str = 'processor-1') -> None:
    sentiment_engine = SentimentEngine()
    rumor_detector = RumorDetector()
    search = EventSearchIndex()
    search.ensure_index()

    def handler(raw: dict) -> None:
        sentiment, impact, confidence, reason = sentiment_engine.score(raw.get('headline', ''))
        rumor = None
        if raw.get('source', '').startswith('Social:'):
            rumor = rumor_detector.score([5, 8, 19], [0.1, -0.2, 0.6], source_count=3)

        with SessionLocal() as db:
            exists = db.scalar(select(Event).where(Event.dedupe_hash == raw['dedupe_hash']))
            if exists:
                return
            event = Event(
                timestamp=datetime.fromisoformat(raw['timestamp']),
                company_name=raw['company_name'],
                ticker=raw['ticker'],
                event_type=raw['event_type'],
                source=raw['source'],
                sentiment=sentiment,
                impact_score=impact,
                confidence_score=confidence,
                sector=raw.get('sector', 'Unknown'),
                description=f"{raw.get('description', '')}\nReason: {reason}",
                url=raw['url'],
                dedupe_hash=raw['dedupe_hash'],
                rumor_probability=rumor,
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            search.index_event(
                {
                    'timestamp': event.timestamp.isoformat(),
                    'ticker': event.ticker,
                    'company_name': event.company_name,
                    'event_type': event.event_type,
                    'sentiment': event.sentiment,
                    'impact_score': event.impact_score,
                    'source': event.source,
                    'description': event.description,
                    'sector': event.sector,
                    'rumor_probability': event.rumor_probability,
                }
            )

    EventConsumer(group='processors', consumer_name=consumer_name).start(handler)

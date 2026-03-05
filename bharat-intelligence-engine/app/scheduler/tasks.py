from celery.schedules import crontab

from app.config import get_settings
from app.workers.celery_worker import celery_app

settings = get_settings()

celery_app.conf.beat_schedule = {
    'scrape-news-every-30s': {
        'task': 'app.workers.celery_worker.scrape_news',
        'schedule': settings.scrape_news_interval_seconds,
    },
    'scrape-filings-every-15s': {
        'task': 'app.workers.celery_worker.scrape_filings',
        'schedule': settings.scrape_filings_interval_seconds,
    },
    'scrape-regulatory-every-2m': {
        'task': 'app.workers.celery_worker.scrape_regulatory',
        'schedule': settings.scrape_regulatory_interval_seconds,
    },
    'scrape-social-every-60s': {
        'task': 'app.workers.celery_worker.scrape_social',
        'schedule': settings.scrape_social_interval_seconds,
    },
    'update-security-master-daily': {
        'task': 'app.workers.celery_worker.update_security_master',
        'schedule': crontab(minute=30, hour=3),
    },
}

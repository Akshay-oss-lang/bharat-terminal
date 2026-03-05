from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Bharat Intelligence Engine'
    environment: str = 'development'

    postgres_url: str = 'postgresql+psycopg2://bharat:bharat@postgres:5432/bharat'
    redis_url: str = 'redis://redis:6379/0'
    kafka_bootstrap_servers: str = 'kafka:9092'
    elasticsearch_url: str = 'http://elasticsearch:9200'

    event_bus_backend: str = 'redis'  # redis|kafka
    event_stream_name: str = 'market_events'
    websocket_channel: str = 'events_ws'

    scrape_news_interval_seconds: int = 30
    scrape_filings_interval_seconds: int = 15
    scrape_social_interval_seconds: int = 60
    scrape_regulatory_interval_seconds: int = 120


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

from elasticsearch import Elasticsearch

from app.config import get_settings

settings = get_settings()


class EventSearchIndex:
    def __init__(self) -> None:
        self.client = Elasticsearch(settings.elasticsearch_url)
        self.index_name = 'events'

    def ensure_index(self) -> None:
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(index=self.index_name)

    def index_event(self, event: dict) -> None:
        self.client.index(index=self.index_name, document=event)

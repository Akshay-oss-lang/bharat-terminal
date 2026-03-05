import logging
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from app.processors.event_extractor import EventExtractor
from app.streaming.event_producer import EventProducer

logger = logging.getLogger(__name__)

NEWS_SOURCES = {
    'Economic Times': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
    'Moneycontrol': 'https://www.moneycontrol.com/rss/latestnews.xml',
    'Reuters': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
}


class NewsScraper:
    def __init__(self) -> None:
        self.extractor = EventExtractor()
        self.producer = EventProducer()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
    def _fetch(self, url: str) -> str:
        headers = {'User-Agent': f'BharatIntelBot/{datetime.utcnow().timestamp()}'}
        with httpx.Client(timeout=15.0, follow_redirects=True, headers=headers) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text

    def run(self) -> int:
        published = 0
        for source, url in NEWS_SOURCES.items():
            try:
                body = self._fetch(url)
                soup = BeautifulSoup(body, 'xml')
                for item in soup.find_all('item')[:20]:
                    headline = item.title.text if item.title else 'Untitled headline'
                    link = item.link.text if item.link else url
                    description = item.description.text if item.description else headline
                    event = self.extractor.extract(source=source, url=link, headline=headline, body=description)
                    self.producer.send(event)
                    published += 1
            except Exception as exc:
                logger.exception('news_source_failed', extra={'source': source, 'error': str(exc)})
        logger.info('news_scrape_complete', extra={'published': published})
        return published

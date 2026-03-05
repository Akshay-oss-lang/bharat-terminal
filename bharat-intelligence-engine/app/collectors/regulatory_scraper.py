import logging

import httpx
from bs4 import BeautifulSoup

from app.processors.event_extractor import EventExtractor
from app.streaming.event_producer import EventProducer

logger = logging.getLogger(__name__)

SOURCES = {
    'SEBI': 'https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&smid=0&ssid=0',
    'RBI': 'https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx',
    'Ministry of Finance': 'https://financialservices.gov.in/latest-updates',
}


class RegulatoryScraper:
    def __init__(self) -> None:
        self.extractor = EventExtractor()
        self.producer = EventProducer()

    def run(self) -> int:
        published = 0
        client = httpx.Client(timeout=20.0, follow_redirects=True, headers={'User-Agent': 'BharatIntelRegBot/1.0'})
        try:
            for source, url in SOURCES.items():
                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for anchor in soup.select('a')[:50]:
                        text = anchor.get_text(' ', strip=True)
                        if len(text) < 25:
                            continue
                        link = anchor.get('href') or url
                        event = self.extractor.extract(source, link, text, text)
                        self.producer.send(event)
                        published += 1
                except Exception as exc:
                    logger.exception('regulatory_source_failed', extra={'source': source, 'error': str(exc)})
        finally:
            client.close()
        return published

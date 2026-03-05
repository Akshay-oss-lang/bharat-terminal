import logging

import scrapy
from scrapy.crawler import CrawlerProcess

from app.processors.event_extractor import EventExtractor
from app.streaming.event_producer import EventProducer

logger = logging.getLogger(__name__)


class FilingsSpider(scrapy.Spider):
    name = 'filings_spider'
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1,
        'RETRY_TIMES': 3,
        'USER_AGENT': 'BharatIntelFilingsBot/1.0',
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },
    }
    start_urls = [
        'https://www.nseindia.com/companies-listing/corporate-filings-announcements',
        'https://www.bseindia.com/corporates/ann.html',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extractor = EventExtractor()
        self.producer = EventProducer()

    def parse(self, response):
        rows = response.css('a::text').getall()
        for title in rows[:30]:
            clean = title.strip()
            if len(clean) < 20:
                continue
            event = self.extractor.extract(
                source='Exchange Filings',
                url=response.url,
                headline=clean,
                body=clean,
            )
            self.producer.send(event)
        logger.info('filings_parsed', extra={'url': response.url, 'records': len(rows)})


def run_filings_scraper() -> None:
    process = CrawlerProcess(settings={'LOG_LEVEL': 'ERROR'})
    process.crawl(FilingsSpider)
    process.start()

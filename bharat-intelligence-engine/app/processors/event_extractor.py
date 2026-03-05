import hashlib
import re
from datetime import datetime

EVENT_KEYWORDS = {
    'earnings': ['earnings', 'quarterly', 'results'],
    'government_contract': ['contract', 'tender', 'award'],
    'regulatory_action': ['sebi', 'rbi', 'penalty', 'order'],
    'management_change': ['appoint', 'resign', 'ceo', 'cfo', 'director'],
    'policy_change': ['policy', 'cabinet', 'notification', 'circular'],
    'insider_activity': ['insider', 'promoter', 'pledge', 'bulk deal', 'block deal'],
    'operational_update': ['production', 'sales update', 'capacity', 'guidance'],
}

TICKER_PATTERN = re.compile(r'\b[A-Z]{2,10}\b')


class EventExtractor:
    def extract(self, source: str, url: str, headline: str, body: str) -> dict:
        text = f'{headline} {body}'.lower()
        event_type = 'general_update'
        for candidate, words in EVENT_KEYWORDS.items():
            if any(word in text for word in words):
                event_type = candidate
                break

        ticker_match = TICKER_PATTERN.findall(headline.upper())
        ticker = ticker_match[0] if ticker_match else 'UNKNOWN'
        company = headline.split('-')[0].strip() if '-' in headline else ticker
        timestamp = datetime.utcnow()
        dedupe_hash = self._dedupe_hash(headline, source, timestamp.isoformat())

        return {
            'timestamp': timestamp.isoformat(),
            'company_name': company,
            'ticker': ticker,
            'event_type': event_type,
            'source': source,
            'headline': headline,
            'description': body[:1500],
            'url': url,
            'sector': 'Unknown',
            'dedupe_hash': dedupe_hash,
        }

    @staticmethod
    def _dedupe_hash(headline: str, source: str, timestamp: str) -> str:
        payload = f'{headline}|{source}|{timestamp}'
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

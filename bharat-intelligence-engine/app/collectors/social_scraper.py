import random
from datetime import datetime

from app.processors.event_extractor import EventExtractor
from app.streaming.event_producer import EventProducer

SOCIAL_CHANNELS = ['Twitter/X', 'Reddit', 'Telegram', 'Discord', 'YouTube']
SAMPLE_POSTS = [
    'DEFENCE PSU sees sudden chatter on large tender win and missile order pipeline',
    'AUTO ANCILLARY supplier rumor: management commentary hints at better margin next quarter',
    'PSU BANK rerating talk intensifies after improving slippage data and treasury gains',
]


class SocialScraper:
    def __init__(self) -> None:
        self.extractor = EventExtractor()
        self.producer = EventProducer()

    def run(self) -> int:
        published = 0
        for channel in SOCIAL_CHANNELS:
            for _ in range(5):
                post = random.choice(SAMPLE_POSTS)
                event = self.extractor.extract(
                    source=f'Social:{channel}',
                    url=f"https://{channel.lower().replace('/', '')}.com/{int(datetime.utcnow().timestamp())}",
                    headline=post,
                    body=post,
                )
                self.producer.send(event)
                published += 1
        return published

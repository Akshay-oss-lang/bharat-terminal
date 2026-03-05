import json
from typing import Generator

from kafka import KafkaConsumer, KafkaProducer
from redis import Redis

from app.config import get_settings

settings = get_settings()


class EventBus:
    def __init__(self) -> None:
        self.backend = settings.event_bus_backend.lower()
        if self.backend == 'kafka':
            self.producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            )
        else:
            self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    def publish(self, event: dict) -> None:
        if self.backend == 'kafka':
            self.producer.send(settings.event_stream_name, event)
            self.producer.flush()
        else:
            self.redis.xadd(settings.event_stream_name, {'payload': json.dumps(event)}, maxlen=100_000, approximate=True)

    def consume(self, group: str, consumer_name: str) -> Generator[dict, None, None]:
        if self.backend == 'kafka':
            consumer = KafkaConsumer(
                settings.event_stream_name,
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=group,
            )
            for msg in consumer:
                yield msg.value
            return

        try:
            self.redis.xgroup_create(settings.event_stream_name, group, id='$', mkstream=True)
        except Exception:
            pass

        while True:
            entries = self.redis.xreadgroup(
                groupname=group,
                consumername=consumer_name,
                streams={settings.event_stream_name: '>'},
                count=100,
                block=5000,
            )
            if not entries:
                continue
            for _, stream_entries in entries:
                for message_id, fields in stream_entries:
                    payload = json.loads(fields['payload'])
                    self.redis.xack(settings.event_stream_name, group, message_id)
                    yield payload

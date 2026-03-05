from collections.abc import Callable

from app.streaming.event_bus import EventBus


class EventConsumer:
    def __init__(self, group: str, consumer_name: str) -> None:
        self.bus = EventBus()
        self.group = group
        self.consumer_name = consumer_name

    def start(self, handler: Callable[[dict], None]) -> None:
        for event in self.bus.consume(group=self.group, consumer_name=self.consumer_name):
            handler(event)

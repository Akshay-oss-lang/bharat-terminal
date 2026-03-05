from app.streaming.event_bus import EventBus


class EventProducer:
    def __init__(self) -> None:
        self.bus = EventBus()

    def send(self, event: dict) -> None:
        self.bus.publish(event)

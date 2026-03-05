import asyncio
import json
import logging
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from redis import Redis
from sqlalchemy import desc, select

from app.api.events_api import router as events_router
from app.api.signals_api import router as signals_router
from app.config import get_settings
from app.database.db_connection import Base, SessionLocal, engine
from app.database.models import Event
from app.utils.logging import configure_logging

settings = get_settings()
configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
app.include_router(events_router)
app.include_router(signals_router)


@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info('startup_complete', extra={'time': datetime.utcnow().isoformat()})


@app.get('/health')
def health() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.websocket('/ws/events')
async def events_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = redis.pubsub()
    pubsub.subscribe(settings.websocket_channel)
    try:
        while True:
            msg = pubsub.get_message(ignore_subscribe_messages=True)
            if msg and msg.get('data'):
                await websocket.send_text(msg['data'])
            else:
                with SessionLocal() as db:
                    latest = db.scalars(select(Event).order_by(desc(Event.timestamp)).limit(1)).first()
                    if latest:
                        await websocket.send_text(json.dumps({'ticker': latest.ticker, 'event_type': latest.event_type}))
                await asyncio.sleep(2)
    except WebSocketDisconnect:
        logger.info('ws_disconnected')
    finally:
        pubsub.close()


@app.post('/internal/publish-latest')
def publish_latest() -> dict:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    with SessionLocal() as db:
        latest = db.scalars(select(Event).order_by(desc(Event.timestamp)).limit(1)).first()
        if latest:
            redis.publish(settings.websocket_channel, json.dumps({'ticker': latest.ticker, 'event_type': latest.event_type}))
            return {'published': True}
    return {'published': False}

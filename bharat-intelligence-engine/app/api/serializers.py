from app.database.models import Event


def event_to_dict(event: Event) -> dict:
    return {
        'id': event.id,
        'timestamp': event.timestamp.isoformat() if event.timestamp else None,
        'company_name': event.company_name,
        'ticker': event.ticker,
        'event_type': event.event_type,
        'source': event.source,
        'sentiment': event.sentiment,
        'impact_score': event.impact_score,
        'confidence_score': event.confidence_score,
        'sector': event.sector,
        'description': event.description,
        'url': event.url,
        'rumor_probability': event.rumor_probability,
        'created_at': event.created_at.isoformat() if event.created_at else None,
    }

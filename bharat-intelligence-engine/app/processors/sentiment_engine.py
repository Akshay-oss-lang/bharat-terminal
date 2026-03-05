POSITIVE_TERMS = {'beat', 'growth', 'record', 'upgrade', 'win', 'order inflow', 'profit rises'}
NEGATIVE_TERMS = {'miss', 'probe', 'downgrade', 'loss widens', 'fraud', 'penalty', 'default'}


class SentimentEngine:
    def score(self, text: str) -> tuple[str, float, float, str]:
        lowered = text.lower()
        pos_hits = sum(1 for term in POSITIVE_TERMS if term in lowered)
        neg_hits = sum(1 for term in NEGATIVE_TERMS if term in lowered)

        if pos_hits > neg_hits:
            sentiment = 'positive'
        elif neg_hits > pos_hits:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        impact = min(100.0, 40.0 + (pos_hits + neg_hits) * 12.5)
        confidence = min(100.0, 55.0 + abs(pos_hits - neg_hits) * 15.0)
        reason = f'Sentiment inferred from positive hits={pos_hits} and negative hits={neg_hits}.'
        return sentiment, impact, confidence, reason

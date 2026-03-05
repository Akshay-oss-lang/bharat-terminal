class OptionsAnomalyDetector:
    def detect(self, volume_ratio: float, oi_change_pct: float, put_call_ratio: float) -> dict:
        score = min(100.0, volume_ratio * 20 + abs(oi_change_pct) * 0.7 + abs(put_call_ratio - 1) * 30)
        direction = 'bullish' if put_call_ratio < 0.9 else 'bearish' if put_call_ratio > 1.2 else 'mixed'
        return {
            'anomaly_score': round(score, 2),
            'direction': direction,
            'reason': 'Derived from unusual volume, OI swing, and put-call skew.',
        }

from statistics import mean


class RumorDetector:
    def score(self, mention_counts: list[int], sentiment_values: list[float], source_count: int) -> float:
        if not mention_counts:
            return 0.0
        latest = mention_counts[-1]
        baseline = mean(mention_counts[:-1]) if len(mention_counts) > 1 else mention_counts[-1]
        spike_ratio = (latest / baseline) if baseline else float(latest)
        sentiment_volatility = abs(sentiment_values[-1] - mean(sentiment_values)) if sentiment_values else 0.0

        score = min(100.0, spike_ratio * 25 + sentiment_volatility * 30 + source_count * 6)
        return round(score, 2)

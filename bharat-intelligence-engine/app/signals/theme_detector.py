from collections import Counter


class ThemeDetector:
    def detect(self, corpus: list[str]) -> list[dict]:
        themes = {
            'defence_sector_growth': ['defence', 'missile', 'military', 'procurement'],
            'railway_infra_spending': ['railway', 'rail', 'locomotive', 'coach'],
            'renewable_energy_investment': ['solar', 'wind', 'renewable', 'green hydrogen'],
            'ai_semiconductor_supply_chain': ['ai', 'chip', 'semiconductor', 'fab'],
            'psu_bank_rerating': ['psu bank', 'public sector bank', 'rerating', 'npa'],
        }
        scores = Counter()
        joined = ' '.join(corpus).lower()
        for name, words in themes.items():
            scores[name] = sum(1 for word in words if word in joined)
        return [
            {'theme': theme, 'score': score}
            for theme, score in scores.most_common()
            if score > 0
        ]

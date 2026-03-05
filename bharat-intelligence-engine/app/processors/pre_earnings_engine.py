class PreEarningsEngine:
    def score(self, sales_growth: float, production_growth: float, inventory_change: float, commodity_tailwind: float) -> dict:
        weighted = (
            sales_growth * 0.35
            + production_growth * 0.25
            - inventory_change * 0.2
            + commodity_tailwind * 0.2
        )
        surprise_probability = max(0.0, min(100.0, 50 + weighted * 5))
        return {
            'surprise_probability': round(surprise_probability, 2),
            'explanation': 'Score blends sales, production, inventory dynamics, and commodity trend impact.',
        }

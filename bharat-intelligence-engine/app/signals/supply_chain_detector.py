class SupplyChainDetector:
    def detect(self, freight_index_change: float, raw_material_change: float, import_dependency: float) -> dict:
        risk = min(100.0, abs(freight_index_change) * 0.4 + abs(raw_material_change) * 0.5 + import_dependency * 0.3)
        status = 'risk' if risk > 60 else 'watch' if risk > 35 else 'stable'
        return {
            'supply_chain_risk': round(risk, 2),
            'status': status,
            'reason': 'Combines freight pressure, input-cost shock, and import dependency.',
        }

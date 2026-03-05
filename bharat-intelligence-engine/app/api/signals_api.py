from fastapi import APIRouter

from app.signals.options_anomaly import OptionsAnomalyDetector
from app.signals.supply_chain_detector import SupplyChainDetector
from app.signals.theme_detector import ThemeDetector

router = APIRouter(prefix='/events', tags=['signals'])


@router.get('/options-activity')
def options_activity(volume_ratio: float = 2.3, oi_change_pct: float = 28, put_call_ratio: float = 0.78):
    return OptionsAnomalyDetector().detect(volume_ratio, oi_change_pct, put_call_ratio)


@router.get('/themes')
def market_themes():
    corpus = [
        'Defence stocks gain after fresh procurement cycle',
        'Railway capex rises in budget, infra companies rally',
        'AI chip and semiconductor policy support manufacturing',
    ]
    return ThemeDetector().detect(corpus)


@router.get('/supply-chain')
def supply_chain(freight_index_change: float = 12, raw_material_change: float = 8, import_dependency: float = 55):
    return SupplyChainDetector().detect(freight_index_change, raw_material_change, import_dependency)

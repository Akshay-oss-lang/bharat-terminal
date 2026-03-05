from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Security

SEED_SECURITIES = [
    ('RELIANCE', 'Reliance Industries Ltd', 'NSE', 'Energy', 'Oil & Gas', 'equity'),
    ('TCS', 'Tata Consultancy Services', 'NSE', 'IT', 'Software Services', 'equity'),
    ('HDFCBANK', 'HDFC Bank Ltd', 'NSE', 'Financials', 'Banks', 'equity'),
    ('NIFTYBEES', 'Nippon India ETF Nifty BeES', 'NSE', 'ETF', 'Index ETF', 'etf'),
    ('IRBInvIT', 'IRB InvIT Fund', 'NSE', 'Infrastructure', 'InvIT', 'invit'),
    ('EMBASSY', 'Embassy Office Parks REIT', 'NSE', 'Real Estate', 'REIT', 'reit'),
    ('7.18GS2033', 'Government Security 2033', 'NSE', 'Debt', 'Government Security', 'gsec'),
    ('NABARD24', 'NABARD Bond 2024', 'BSE', 'Debt', 'Corporate Bond', 'corporate_bond'),
]


class SecurityMasterUpdater:
    def run(self, db: Session) -> int:
        changed = 0
        for ticker, company, exchange, sector, industry, instrument in SEED_SECURITIES:
            existing = db.scalar(select(Security).where(Security.ticker == ticker, Security.exchange == exchange))
            if not existing:
                db.add(
                    Security(
                        ticker=ticker,
                        company_name=company,
                        exchange=exchange,
                        sector=sector,
                        industry=industry,
                        instrument_type=instrument,
                        listing_date=date(2010, 1, 1),
                    )
                )
                changed += 1
                continue
            existing.company_name = company
            existing.sector = sector
            existing.industry = industry
            existing.instrument_type = instrument
        db.commit()
        return changed

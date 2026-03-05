# Bharat Intelligence Engine

AI-driven market intelligence and event detection backend for BharatTerminal, covering NSE/BSE equities, SME, ETFs, mutual funds, corporate bonds, government securities, REITs, and InvITs.

## Architecture

`Scrapers -> Event Bus (Redis Streams/Kafka) -> AI Processing Workers -> PostgreSQL + Elasticsearch -> FastAPI + WebSockets`

## Features

- Continuous ingestion from news, filings, regulatory and social sources.
- Event extraction with deduplication (`headline+source+timestamp` hash).
- AI scoring: sentiment, impact, confidence, rumor probability.
- Signal engines: options anomalies, supply-chain risk, theme detection, pre-earnings analytics.
- Security master maintenance for Indian listed instruments.
- Real-time websocket feed and REST endpoints used by BharatTerminal.

## Project layout

See `app/` for modules:

- `collectors/` Scrapy/Playwright + HTTP collectors
- `streaming/` Kafka/Redis stream abstraction
- `processors/` Event extraction and scoring engines
- `signals/` Quant signal calculators
- `backtesting/` Historical reaction calibration
- `database/` SQLAlchemy and Elasticsearch indexing
- `api/` FastAPI routes
- `workers/` Celery tasks + stream processor
- `scheduler/` Beat schedules
- `security_master/` daily universe updater

## Endpoints

- `GET /events/latest`
- `GET /events/high-impact`
- `GET /events/company/{ticker}`
- `GET /events/sector/{sector}`
- `GET /events/rumor-signals`
- `GET /events/pre-earnings`
- `GET /events/options-activity`
- `GET /events/themes`
- `GET /events/supply-chain`
- `GET /health`
- `WS /ws/events`

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Then open:
- API docs: `http://localhost:8000/docs`
- Elasticsearch: `http://localhost:9200`

## Processing loop

- News scrape interval: 30 sec
- Filings scrape interval: 15 sec
- Social scrape interval: 60 sec
- Regulatory scrape interval: 120 sec

Configured in `app/config.py` and `app/scheduler/tasks.py`.

# SentinelOSINT

[![CI](https://github.com/ESTROC/sentinel-osint/actions/workflows/ci.yml/badge.svg)](https://github.com/ESTROC/sentinel-osint/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688)

**Defensive open-source security intelligence and situational-awareness workbench.**

SentinelOSINT turns public security signals into a structured analyst workflow: **collect → normalize → assess → corroborate → document → monitor / escalate**.

It is built as a portfolio-grade full-stack system with a **Next.js analyst interface**, **FastAPI intelligence API**, source attribution, transparent scoring, analyst triage, evidence tracking, audit history, incident briefs, and optional **serverless PostgreSQL** persistence.

> **Scope:** defensive OSINT and security-event monitoring only. Synthetic scenarios are clearly marked. Open-web discovery is never treated as verified by default, and the project does not target private individuals or bypass access controls.

## What it demonstrates

Security teams rarely need another feed. They need a repeatable process for answering:

- What happened?
- How reliable is the current information?
- What remains unverified?
- Could a monitored asset be affected?
- What should be reviewed first?
- What evidence supports or contradicts the current assessment?
- What did the analyst do, and when?
- Should the event be monitored, escalated, or closed?

SentinelOSINT models that workflow directly.

## Core capabilities

### Analyst workbench
- global situational map with event and fictional demo-asset overlays
- prioritized incident queue with search and filtering
- event detail records with source, time, location, confidence, and proximity context
- triage states: `NEW → REVIEWING → MONITORING → ESCALATED → CLOSED`
- escalation levels: `NONE / WATCH / MANAGER_REVIEW / IMMEDIATE`
- analyst verification, notes, and evidence records
- audit trail for analyst actions
- structured incident briefs separating facts, gaps, source assessment, relevance, and recommended action

### Public-source collection
Implemented connectors include:

| Source | Purpose |
|---|---|
| **USGS Earthquake Hazards Program** | Authoritative seismic events |
| **CISA Known Exploited Vulnerabilities** | Actively exploited cyber vulnerabilities |
| **GDACS** | Global disaster alerts |
| **GDELT DOC 2.0** | Open-web and news discovery for security-relevant reporting |

Open-web discovery receives lower initial confidence and remains explicitly unverified until reviewed.

### Explainable prioritization

The queue score is deterministic and documented:

```text
priority = 30% severity
         + 25% potential impact
         + 20% confidence
         + 15% recency
         + 10% proximity to a fictional demo asset
```

Priority organizes analyst attention. It does **not** establish whether a report is true.

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Analyst UI                      │
│ Dashboard · Map · Queue · Event Record · Analyst Workbench │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI API                          │
│ Events · Metrics · Sources · Assets · Triage · Evidence    │
│ Briefing · Audit · Live Ingestion                          │
└───────────────┬──────────────────────────────┬──────────────┘
                │                              │
                ▼                              ▼
┌──────────────────────────┐       ┌──────────────────────────┐
│ Serverless PostgreSQL    │       │ Public Source Connectors │
│ Neon / Supabase pooler   │       │ USGS · CISA · GDACS ·    │
│ Optional for persistence │       │ GDELT                     │
└──────────────────────────┘       └──────────────────────────┘
```

The API falls back to deterministic synthetic in-memory scenarios when `DATABASE_URL` is not configured, keeping code review and demos reliable without pretending synthetic records are real events.

## Repository structure

```text
sentinel-osint/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   ├── tests/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── vercel.json
│   └── web/                    # Next.js analyst interface
│       ├── app/
│       ├── components/
│       ├── lib/
│       ├── package.json
│       └── vercel.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ANALYST_WORKFLOW.md
│   ├── SOURCE_POLICY.md
│   └── DEPLOYMENT.md
└── .github/workflows/ci.yml
```

## Local development

### API

```bash
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

OpenAPI documentation: `http://localhost:8000/docs`

### Web

```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

Set:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Open `http://localhost:3000`.

## Vercel deployment

The monorepo is designed for **two Vercel projects from the same Git repository**:

1. backend root: `apps/api`
2. frontend root: `apps/web`

For persistent analyst actions and ingested events, configure a serverless Postgres pooler URL. Full setup is in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## API surface

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/health` | runtime and storage health |
| `GET` | `/api/metrics` | queue metrics |
| `GET` | `/api/assets` | fictional demo assets |
| `GET` | `/api/sources` | source catalog |
| `GET` | `/api/events` | prioritized event queue |
| `GET` | `/api/events/{id}` | event record |
| `PATCH` | `/api/events/{id}` | analyst status, escalation, verification, notes |
| `GET/POST` | `/api/events/{id}/evidence` | evidence ledger |
| `GET` | `/api/events/{id}/audit` | analyst audit trail |
| `GET` | `/api/events/{id}/brief` | structured incident brief |
| `POST` | `/api/ingest` | bounded live-source ingestion |

## Verification model

SentinelOSINT intentionally separates:

1. **source type**
2. **confidence**
3. **corroborating evidence**
4. **analyst verification**
5. **priority / organizational relevance**

That prevents a common analytical failure: treating a high-priority or frequently repeated claim as automatically verified.

## Security and safety

- no credential scraping or authentication bypass
- no private-account collection
- no doxxing or individual targeting workflow
- no biometric identification
- configurable CORS
- bounded outbound source requests with explicit timeouts
- optional analyst-key protection for mutation routes
- no persistent local filesystem dependency
- source-specific failures are isolated instead of failing the full ingestion job
- synthetic records are explicit in both API and UI

See [docs/SOURCE_POLICY.md](docs/SOURCE_POLICY.md).

## Quality

Backend tests cover:
- scoring thresholds
- proximity scoring
- API health
- event retrieval
- metrics
- incident brief generation
- analyst update flow

The GitHub Actions workflow runs Python tests, TypeScript checks, and a production Next.js build.

## Technology

**Frontend:** Next.js, React, TypeScript, Leaflet / OpenStreetMap, Lucide  
**Backend:** FastAPI, Pydantic, HTTPX, Python  
**Data:** PostgreSQL via Psycopg; in-memory demo fallback  
**Deployment:** Vercel frontend + Vercel Python backend  
**Quality:** Pytest, GitHub Actions, typed models, documented analyst methodology

## Author

**Ayush Tripathi** · [LinkedIn](https://www.linkedin.com/in/cdtayush/) · [GitHub](https://github.com/ESTROC)

## License

MIT License.

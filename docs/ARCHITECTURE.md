# Architecture

SentinelOSINT is a two-application monorepo designed for independent Vercel deployments.

## Frontend

`apps/web` is a Next.js analyst workbench. It consumes the public read API directly and falls back to bundled synthetic scenarios if the backend is unavailable. This keeps portfolio demonstrations reliable without hiding connectivity state.

Main views:
- operations dashboard
- situational map
- analyst incident queue
- event detail record
- analyst workbench
- structured incident brief
- methodology and ethics page

## Backend

`apps/api` is a FastAPI service. It owns:
- event models and validation
- source collection
- deterministic scoring
- asset-proximity analysis
- triage state
- evidence records
- audit records
- incident brief generation
- persistence abstraction

## Storage modes

### Demo memory mode
Used when `DATABASE_URL` is absent. The API boots with a deterministic synthetic dataset and fictional corporate assets. This mode is ideal for code review and portfolio demos.

### PostgreSQL mode
Used when `DATABASE_URL` is present. The backend creates a compact JSONB-backed schema for events, assets, evidence, and audit records. The design is suitable for serverless Postgres pooler endpoints such as Neon or Supabase.

The event JSON is persisted alongside indexed columns for priority, time, status, escalation, and synthetic flag.

## Serverless considerations

- no dependency on a persistent local filesystem
- bounded live-source result count
- outbound requests have explicit timeouts
- source failures are isolated
- database connections are opened per repository operation and closed immediately
- scoring is recomputed on reads without generating write-on-read traffic
- frontend and backend are deployable separately from one Git repository

## Trust model

The system deliberately distinguishes:
- discovery from verification
- priority from truth
- source authority from organizational impact
- machine scoring from analyst judgment

That separation is central to the project, not an afterthought.

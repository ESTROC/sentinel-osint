# Vercel Deployment

SentinelOSINT is designed as a two-project Vercel deployment from one Git repository.

## 1. API project

Import the repository and set the **Root Directory** to:

```
apps/api
```

Vercel detects the FastAPI entrypoint in `main.py`.

Recommended environment variables:

```env
ENVIRONMENT=production
DATABASE_URL=<serverless-postgres-pooler-url>
ANALYST_API_KEY=<strong-random-secret>
ALLOWED_ORIGINS=https://<web-project>.vercel.app
ALLOW_PUBLIC_DEMO_WRITES=false
SOURCE_TIMEOUT_SECONDS=12
MAX_LIVE_ITEMS_PER_SOURCE=30
```

For a read/write portfolio demo without persistent storage, omit `DATABASE_URL` and leave `ALLOW_PUBLIC_DEMO_WRITES=true`. The API then uses deterministic synthetic in-memory scenarios.

## 2. Web project

Import the same repository as a second Vercel project and set the **Root Directory** to:

```
apps/web
```

Add:

```env
NEXT_PUBLIC_API_BASE_URL=https://<api-project>.vercel.app
```

The UI has a bundled fallback dataset, so the interface remains reviewable if the API is temporarily unavailable. The fallback is visibly labeled as demo mode.

## 3. Persistent data

For persistent analyst actions, evidence, audit logs, and ingested live events, use a serverless PostgreSQL pooler URL such as Neon or Supabase.

The backend does not rely on local filesystem persistence, which makes it suitable for serverless execution.

## 4. Recommended production posture

- set a strong `ANALYST_API_KEY`
- restrict `ALLOWED_ORIGINS` to the deployed web URL
- set `ALLOW_PUBLIC_DEMO_WRITES=false`
- keep public GET endpoints open for portfolio review
- do not expose private or restricted-source credentials

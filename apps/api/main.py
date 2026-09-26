from __future__ import annotations

from functools import lru_cache
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import AuditRecord, EvidenceCreate, EventCategory, EventStatus, EventUpdate, IngestRequest, PriorityLabel
from app.repository import MemoryRepository, PostgresRepository, Repository
from app.scoring import score_event
from app.service import add_evidence, compute_metrics, incident_brief, rescore_all, update_event
from app.sources import SOURCE_CATALOG, collect_sources

app = FastAPI(
    title="SentinelOSINT API",
    version="1.0.0",
    description="Defensive open-source security-event monitoring, triage, and incident-briefing API.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def get_repo() -> Repository:
    if settings.database_url:
        return PostgresRepository(settings.database_url)
    return MemoryRepository()


def require_write_access(x_analyst_key: str | None = Header(default=None)) -> None:
    if settings.allow_public_demo_writes and not settings.database_url:
        return
    if settings.analyst_api_key and x_analyst_key == settings.analyst_api_key:
        return
    raise HTTPException(status_code=401, detail="Analyst write access required")


@app.get("/")
def root():
    return {"name": settings.app_name, "status": "ok", "docs": "/docs", "mode": "postgres" if settings.database_url else "demo-memory"}


@app.get("/api/health")
def health(repo: Repository = Depends(get_repo)):
    return {"status": "ok", "environment": settings.environment, "storage": "postgres" if settings.database_url else "memory-demo", "events": len(repo.list_events())}


@app.get("/api/metrics")
def metrics(repo: Repository = Depends(get_repo)):
    events = rescore_all(repo)
    return compute_metrics(events)


@app.get("/api/assets")
def assets(repo: Repository = Depends(get_repo)):
    return repo.list_assets()


@app.get("/api/sources")
def sources():
    return SOURCE_CATALOG


@app.get("/api/events")
def list_events(
    priority: PriorityLabel | None = Query(default=None),
    status: EventStatus | None = Query(default=None),
    category: EventCategory | None = Query(default=None),
    synthetic: bool | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    repo: Repository = Depends(get_repo),
):
    events = rescore_all(repo)
    if priority:
        events = [e for e in events if e.priority == priority]
    if status:
        events = [e for e in events if e.status == status]
    if category:
        events = [e for e in events if e.category == category]
    if synthetic is not None:
        events = [e for e in events if e.synthetic == synthetic]
    return events[:limit]


@app.get("/api/events/{event_id}")
def get_event(event_id: str, repo: Repository = Depends(get_repo)):
    event = repo.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return score_event(event, repo.list_assets())


@app.patch("/api/events/{event_id}", dependencies=[Depends(require_write_access)])
def patch_event(event_id: str, patch: EventUpdate, repo: Repository = Depends(get_repo)):
    event = update_event(repo, event_id, patch)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return score_event(event, repo.list_assets())


@app.get("/api/events/{event_id}/evidence")
def event_evidence(event_id: str, repo: Repository = Depends(get_repo)):
    if not repo.get_event(event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return repo.list_evidence(event_id)


@app.post("/api/events/{event_id}/evidence", dependencies=[Depends(require_write_access)])
def create_evidence(event_id: str, request: EvidenceCreate, repo: Repository = Depends(get_repo)):
    evidence = add_evidence(repo, event_id, request)
    if not evidence:
        raise HTTPException(status_code=404, detail="Event not found")
    return evidence


@app.get("/api/events/{event_id}/audit")
def event_audit(event_id: str, repo: Repository = Depends(get_repo)):
    if not repo.get_event(event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return repo.list_audit(event_id)


@app.get("/api/events/{event_id}/brief")
def brief(event_id: str, repo: Repository = Depends(get_repo)):
    event = repo.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event = score_event(event, repo.list_assets())
    return incident_brief(repo, event)


@app.post("/api/ingest", dependencies=[Depends(require_write_access)])
async def ingest(request: IngestRequest, repo: Repository = Depends(get_repo)):
    events, errors = await collect_sources(request.sources)
    assets = repo.list_assets()
    scored = [score_event(event, assets) for event in events]
    count = repo.upsert_events(scored)
    for event in scored[:20]:
        repo.add_audit(AuditRecord(id=str(uuid4()), event_id=event.id, actor=request.actor, action="SOURCE_INGESTED", detail=f"Ingested from {event.source_name}; source_type={event.source_type}"))
    return {"ingested": count, "errors": errors, "sources_requested": request.sources}

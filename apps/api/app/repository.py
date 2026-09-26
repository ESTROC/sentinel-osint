from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from threading import RLock
from typing import Iterable

from .demo_data import DEMO_ASSETS, DEMO_EVENTS
from .models import Asset, AuditRecord, Evidence, SecurityEvent


class Repository(ABC):
    @abstractmethod
    def list_events(self) -> list[SecurityEvent]: ...
    @abstractmethod
    def get_event(self, event_id: str) -> SecurityEvent | None: ...
    @abstractmethod
    def upsert_events(self, events: Iterable[SecurityEvent]) -> int: ...
    @abstractmethod
    def save_event(self, event: SecurityEvent) -> None: ...
    @abstractmethod
    def list_assets(self) -> list[Asset]: ...
    @abstractmethod
    def add_evidence(self, evidence: Evidence) -> Evidence: ...
    @abstractmethod
    def list_evidence(self, event_id: str) -> list[Evidence]: ...
    @abstractmethod
    def add_audit(self, record: AuditRecord) -> AuditRecord: ...
    @abstractmethod
    def list_audit(self, event_id: str) -> list[AuditRecord]: ...


class MemoryRepository(Repository):
    def __init__(self) -> None:
        self._lock = RLock()
        self._events = {event.id: deepcopy(event) for event in DEMO_EVENTS}
        self._assets = deepcopy(DEMO_ASSETS)
        self._evidence: dict[str, list[Evidence]] = {}
        self._audit: dict[str, list[AuditRecord]] = {}

    def list_events(self) -> list[SecurityEvent]:
        with self._lock:
            return deepcopy(list(self._events.values()))

    def get_event(self, event_id: str) -> SecurityEvent | None:
        with self._lock:
            event = self._events.get(event_id)
            return deepcopy(event) if event else None

    def upsert_events(self, events: Iterable[SecurityEvent]) -> int:
        count = 0
        with self._lock:
            for event in events:
                self._events[event.id] = deepcopy(event)
                count += 1
        return count

    def save_event(self, event: SecurityEvent) -> None:
        with self._lock:
            self._events[event.id] = deepcopy(event)

    def list_assets(self) -> list[Asset]:
        return deepcopy(self._assets)

    def add_evidence(self, evidence: Evidence) -> Evidence:
        with self._lock:
            self._evidence.setdefault(evidence.event_id, []).append(deepcopy(evidence))
        return evidence

    def list_evidence(self, event_id: str) -> list[Evidence]:
        with self._lock:
            return deepcopy(self._evidence.get(event_id, []))

    def add_audit(self, record: AuditRecord) -> AuditRecord:
        with self._lock:
            self._audit.setdefault(record.event_id, []).append(deepcopy(record))
        return record

    def list_audit(self, event_id: str) -> list[AuditRecord]:
        with self._lock:
            return deepcopy(self._audit.get(event_id, []))


class PostgresRepository(Repository):
    """Small raw-SQL repository designed for serverless Postgres (Neon/Supabase pooler URLs)."""

    def __init__(self, database_url: str) -> None:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError("psycopg is required when DATABASE_URL is configured") from exc
        self.psycopg = psycopg
        self.dict_row = dict_row
        self.database_url = database_url
        self._ensure_schema()
        self._seed_assets()
        self._seed_demo_events_if_empty()

    def _connect(self):
        return self.psycopg.connect(self.database_url, row_factory=self.dict_row, connect_timeout=8)

    def _ensure_schema(self) -> None:
        statements = [
            """CREATE TABLE IF NOT EXISTS assets (id TEXT PRIMARY KEY, payload JSONB NOT NULL);""",
            """CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, payload JSONB NOT NULL, event_time TIMESTAMPTZ NOT NULL, priority_score DOUBLE PRECISION NOT NULL DEFAULT 0, priority TEXT NOT NULL DEFAULT 'LOW', status TEXT NOT NULL DEFAULT 'NEW', escalation TEXT NOT NULL DEFAULT 'NONE', synthetic BOOLEAN NOT NULL DEFAULT FALSE);""",
            """CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, event_id TEXT NOT NULL, payload JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());""",
            """CREATE TABLE IF NOT EXISTS audit_log (id TEXT PRIMARY KEY, event_id TEXT NOT NULL, payload JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());""",
            """CREATE INDEX IF NOT EXISTS idx_events_priority ON events(priority_score DESC);""",
            """CREATE INDEX IF NOT EXISTS idx_events_event_time ON events(event_time DESC);""",
            """CREATE INDEX IF NOT EXISTS idx_evidence_event_id ON evidence(event_id);""",
            """CREATE INDEX IF NOT EXISTS idx_audit_event_id ON audit_log(event_id);""",
        ]
        with self._connect() as conn:
            with conn.cursor() as cur:
                for statement in statements:
                    cur.execute(statement)
            conn.commit()

    @staticmethod
    def _json(model) -> str:
        return model.model_dump_json()

    def _seed_assets(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                for asset in DEMO_ASSETS:
                    cur.execute("INSERT INTO assets(id,payload) VALUES (%s,%s::jsonb) ON CONFLICT (id) DO NOTHING", (asset.id, self._json(asset)))
            conn.commit()

    def _seed_demo_events_if_empty(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS n FROM events")
                if cur.fetchone()["n"] == 0:
                    for event in DEMO_EVENTS:
                        self._upsert_event_cursor(cur, event)
            conn.commit()

    def _upsert_event_cursor(self, cur, event: SecurityEvent) -> None:
        cur.execute(
            """INSERT INTO events(id,payload,event_time,priority_score,priority,status,escalation,synthetic)
               VALUES (%s,%s::jsonb,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (id) DO UPDATE SET payload=EXCLUDED.payload,event_time=EXCLUDED.event_time,
               priority_score=EXCLUDED.priority_score,priority=EXCLUDED.priority,status=EXCLUDED.status,
               escalation=EXCLUDED.escalation,synthetic=EXCLUDED.synthetic""",
            (event.id, self._json(event), event.event_time, event.priority_score, event.priority.value, event.status.value, event.escalation.value, event.synthetic),
        )

    def list_events(self) -> list[SecurityEvent]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT payload FROM events ORDER BY priority_score DESC, event_time DESC")
            return [SecurityEvent.model_validate(row["payload"]) for row in cur.fetchall()]

    def get_event(self, event_id: str) -> SecurityEvent | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT payload FROM events WHERE id=%s", (event_id,))
            row = cur.fetchone()
            return SecurityEvent.model_validate(row["payload"]) if row else None

    def upsert_events(self, events: Iterable[SecurityEvent]) -> int:
        count = 0
        with self._connect() as conn:
            with conn.cursor() as cur:
                for event in events:
                    self._upsert_event_cursor(cur, event)
                    count += 1
            conn.commit()
        return count

    def save_event(self, event: SecurityEvent) -> None:
        self.upsert_events([event])

    def list_assets(self) -> list[Asset]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT payload FROM assets ORDER BY id")
            return [Asset.model_validate(row["payload"]) for row in cur.fetchall()]

    def add_evidence(self, evidence: Evidence) -> Evidence:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO evidence(id,event_id,payload) VALUES (%s,%s,%s::jsonb)", (evidence.id, evidence.event_id, self._json(evidence)))
            conn.commit()
        return evidence

    def list_evidence(self, event_id: str) -> list[Evidence]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT payload FROM evidence WHERE event_id=%s ORDER BY created_at", (event_id,))
            return [Evidence.model_validate(row["payload"]) for row in cur.fetchall()]

    def add_audit(self, record: AuditRecord) -> AuditRecord:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO audit_log(id,event_id,payload) VALUES (%s,%s,%s::jsonb)", (record.id, record.event_id, self._json(record)))
            conn.commit()
        return record

    def list_audit(self, event_id: str) -> list[AuditRecord]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT payload FROM audit_log WHERE event_id=%s ORDER BY created_at", (event_id,))
            return [AuditRecord.model_validate(row["payload"]) for row in cur.fetchall()]

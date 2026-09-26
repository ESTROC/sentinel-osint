from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class EventCategory(str, Enum):
    CIVIL_UNREST = "Civil Unrest"
    TERRORISM_CONFLICT = "Terrorism / Armed Conflict"
    CRIME_PUBLIC_SAFETY = "Crime / Public Safety"
    NATURAL_DISASTER = "Natural Disaster"
    INFRASTRUCTURE = "Infrastructure Disruption"
    CYBER = "Cybersecurity Event"
    TRANSPORT = "Aviation / Transport Disruption"
    OTHER = "Other Security Event"


class EventStatus(str, Enum):
    NEW = "NEW"
    REVIEWING = "REVIEWING"
    MONITORING = "MONITORING"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"


class EscalationLevel(str, Enum):
    NONE = "NONE"
    WATCH = "WATCH"
    MANAGER_REVIEW = "MANAGER_REVIEW"
    IMMEDIATE = "IMMEDIATE"


class PriorityLabel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Asset(BaseModel):
    id: str
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    criticality: int = Field(ge=1, le=5)
    asset_type: str


class Evidence(BaseModel):
    id: str
    event_id: str
    source_name: str
    source_url: str | None = None
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    note: str = ""
    corroborates: bool = True


class AuditRecord(BaseModel):
    id: str
    event_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str = "demo-analyst"
    action: str
    detail: str


class SecurityEvent(BaseModel):
    id: str
    title: str
    summary: str
    category: EventCategory
    event_time: datetime
    detected_at: datetime
    country: str
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    source_name: str
    source_url: str | None = None
    source_type: str
    severity: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0.0, le=1.0)
    impact: int = Field(ge=1, le=5)
    status: EventStatus = EventStatus.NEW
    escalation: EscalationLevel = EscalationLevel.NONE
    analyst_notes: str = ""
    verified: bool = False
    nearest_asset_id: str | None = None
    nearest_asset_name: str | None = None
    distance_km: float | None = None
    priority_score: float = 0.0
    priority: PriorityLabel = PriorityLabel.LOW
    tags: list[str] = Field(default_factory=list)
    synthetic: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventUpdate(BaseModel):
    status: EventStatus | None = None
    escalation: EscalationLevel | None = None
    analyst_notes: str | None = None
    verified: bool | None = None
    actor: str = "demo-analyst"


class EvidenceCreate(BaseModel):
    source_name: str
    source_url: str | None = None
    note: str = ""
    corroborates: bool = True
    actor: str = "demo-analyst"


class IngestRequest(BaseModel):
    sources: list[str] = Field(default_factory=lambda: ["usgs", "cisa", "gdacs", "gdelt"])
    actor: str = "demo-analyst"


class Metrics(BaseModel):
    total_events: int
    critical_events: int
    high_events: int
    escalated_events: int
    monitoring_events: int
    verified_events: int
    synthetic_events: int
    source_count: int
    category_breakdown: dict[str, int]


class SourceStatus(BaseModel):
    id: str
    name: str
    description: str
    endpoint: str
    category_focus: list[str]
    enabled: bool = True
    live_supported: bool = True


class IncidentBrief(BaseModel):
    event_id: str
    generated_at: datetime
    title: str
    executive_summary: str
    known_facts: list[str]
    information_gaps: list[str]
    source_assessment: str
    organizational_relevance: str
    analyst_action: str
    source_links: list[str]

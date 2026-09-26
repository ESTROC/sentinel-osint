from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .models import AuditRecord, Evidence, EvidenceCreate, EventUpdate, IncidentBrief, Metrics, SecurityEvent
from .repository import Repository
from .scoring import score_event


def rescore_all(repo: Repository) -> list[SecurityEvent]:
    """Recompute queue priority without creating write-on-read database traffic."""
    assets = repo.list_assets()
    events = [score_event(event, assets) for event in repo.list_events()]
    return sorted(events, key=lambda e: (e.priority_score, e.event_time.timestamp()), reverse=True)


def update_event(repo: Repository, event_id: str, patch: EventUpdate) -> SecurityEvent | None:
    event = repo.get_event(event_id)
    if not event:
        return None
    changes: list[str] = []
    for field in ("status", "escalation", "analyst_notes", "verified"):
        value = getattr(patch, field)
        if value is not None and getattr(event, field) != value:
            changes.append(f"{field}: {getattr(event, field)} -> {value}")
            setattr(event, field, value)
    repo.save_event(event)
    if changes:
        repo.add_audit(AuditRecord(id=str(uuid4()), event_id=event_id, actor=patch.actor, action="EVENT_UPDATED", detail="; ".join(changes)))
    return event


def add_evidence(repo: Repository, event_id: str, request: EvidenceCreate) -> Evidence | None:
    if not repo.get_event(event_id):
        return None
    evidence = Evidence(id=str(uuid4()), event_id=event_id, source_name=request.source_name, source_url=request.source_url, note=request.note, corroborates=request.corroborates)
    repo.add_evidence(evidence)
    repo.add_audit(AuditRecord(id=str(uuid4()), event_id=event_id, actor=request.actor, action="EVIDENCE_ADDED", detail=f"Added evidence from {request.source_name}; corroborates={request.corroborates}"))
    return evidence


def compute_metrics(events: list[SecurityEvent]) -> Metrics:
    categories: dict[str, int] = {}
    for event in events:
        categories[event.category.value] = categories.get(event.category.value, 0) + 1
    return Metrics(
        total_events=len(events),
        critical_events=sum(e.priority.value == "CRITICAL" for e in events),
        high_events=sum(e.priority.value == "HIGH" for e in events),
        escalated_events=sum(e.status.value == "ESCALATED" for e in events),
        monitoring_events=sum(e.status.value == "MONITORING" for e in events),
        verified_events=sum(e.verified for e in events),
        synthetic_events=sum(e.synthetic for e in events),
        source_count=len({e.source_name for e in events}),
        category_breakdown=categories,
    )


def incident_brief(repo: Repository, event: SecurityEvent) -> IncidentBrief:
    evidence = repo.list_evidence(event.id)
    corroborating = [e for e in evidence if e.corroborates]
    known = [
        f"Event category: {event.category.value}.",
        f"Event time: {event.event_time.isoformat()}.",
        f"Primary source: {event.source_name}.",
        f"Analyst priority: {event.priority.value} ({event.priority_score:.1f}/100).",
    ]
    if event.city:
        known.append(f"Reported location: {event.city}, {event.country}.")
    if event.nearest_asset_name and event.distance_km is not None:
        known.append(f"Nearest demo asset: {event.nearest_asset_name}, approximately {event.distance_km:.1f} km away.")
    gaps: list[str] = []
    if not event.verified:
        gaps.append("Analyst verification is not complete.")
    if len(corroborating) == 0 and event.source_type == "OPEN_WEB_DISCOVERY":
        gaps.append("No independent corroborating evidence has been attached.")
    if event.latitude is None:
        gaps.append("Precise geolocation is not available from the current source record.")
    if not gaps:
        gaps.append("Continue monitoring for material changes, contradictory reporting, or operational impact.")
    source_assessment = f"Primary confidence is {event.confidence:.0%}. "
    if event.source_type in {"OFFICIAL", "OFFICIAL/INTERGOVERNMENTAL"}:
        source_assessment += "The primary record is an authoritative or official-source feed; downstream impact still requires contextual assessment."
    else:
        source_assessment += "Open-web discovery is not treated as independently verified; review original reporting and corroborate before escalation."
    relevance = "No demo-asset proximity is available."
    if event.nearest_asset_name and event.distance_km is not None:
        relevance = f"The nearest fictional demo asset is {event.nearest_asset_name}, approximately {event.distance_km:.1f} km from the reported coordinates."
    action = {
        "CRITICAL": "Immediate analyst review and escalation; maintain active monitoring and update stakeholders as verified information changes.",
        "HIGH": "Prioritize analyst review, corroborate material details, and consider manager escalation based on confirmed impact.",
        "MEDIUM": "Monitor for escalation indicators and corroborate material changes before raising alert level.",
        "LOW": "Retain in the monitoring queue; reassess if severity, confidence, or proximity changes.",
    }[event.priority.value]
    links = [link for link in [event.source_url, *[e.source_url for e in evidence]] if link]
    return IncidentBrief(
        event_id=event.id,
        generated_at=datetime.now(timezone.utc),
        title=event.title,
        executive_summary=event.summary,
        known_facts=known,
        information_gaps=gaps,
        source_assessment=source_assessment,
        organizational_relevance=relevance,
        analyst_action=action,
        source_links=list(dict.fromkeys(links)),
    )

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from .models import Asset, EscalationLevel, EventCategory, EventStatus, SecurityEvent

NOW = datetime.now(timezone.utc)

DEMO_ASSETS = [
    Asset(id="asset-gurgaon", name="Demo Gurgaon Operations Center", city="Gurgaon", country="India", latitude=28.4595, longitude=77.0266, criticality=5, asset_type="Operations Center"),
    Asset(id="asset-noida", name="Demo Noida Technology Hub", city="Noida", country="India", latitude=28.5355, longitude=77.3910, criticality=4, asset_type="Technology Hub"),
    Asset(id="asset-hyderabad", name="Demo Hyderabad Delivery Center", city="Hyderabad", country="India", latitude=17.3850, longitude=78.4867, criticality=4, asset_type="Delivery Center"),
    Asset(id="asset-bengaluru", name="Demo Bengaluru Engineering Hub", city="Bengaluru", country="India", latitude=12.9716, longitude=77.5946, criticality=4, asset_type="Engineering Hub"),
]


def ev(event_id: str, title: str, summary: str, category: EventCategory, hours_ago: int, country: str, city: str, lat: float, lon: float, severity: int, confidence: float, impact: int, tags: list[str], *, status=EventStatus.NEW, escalation=EscalationLevel.NONE) -> SecurityEvent:
    return SecurityEvent(
        id=event_id,
        title=title,
        summary=summary,
        category=category,
        event_time=NOW - timedelta(hours=hours_ago),
        detected_at=NOW - timedelta(hours=max(hours_ago - 1, 0)),
        country=country,
        city=city,
        latitude=lat,
        longitude=lon,
        source_name="Synthetic Scenario Feed",
        source_url=None,
        source_type="DEMO",
        severity=severity,
        confidence=confidence,
        impact=impact,
        tags=tags,
        status=status,
        escalation=escalation,
        synthetic=True,
        metadata={"scenario": True, "disclaimer": "Synthetic event for portfolio demonstration only."},
    )


DEMO_EVENTS = [
    ev("demo-001", "Civil unrest disrupts arterial routes near business district", "Large demonstrations and temporary road closures create employee-travel and access concerns near a fictional corporate operating area.", EventCategory.CIVIL_UNREST, 2, "India", "Gurgaon", 28.4720, 77.0610, 4, 0.86, 4, ["civil-unrest", "travel", "access"], status=EventStatus.REVIEWING, escalation=EscalationLevel.MANAGER_REVIEW),
    ev("demo-002", "Severe weather produces localized flooding and transport delays", "Heavy rainfall is causing waterlogging, traffic disruption, and intermittent access constraints near a fictional delivery center.", EventCategory.NATURAL_DISASTER, 4, "India", "Hyderabad", 17.4100, 78.4700, 3, 0.91, 4, ["flood", "weather", "transport"], status=EventStatus.MONITORING, escalation=EscalationLevel.WATCH),
    ev("demo-003", "Critical vulnerability added to active exploitation watchlist", "A newly tracked vulnerability affecting a common enterprise component is being reviewed for potential relevance to the demo technology estate.", EventCategory.CYBER, 5, "Global", "Online", 28.5355, 77.3910, 5, 0.95, 5, ["cyber", "vulnerability", "kev"], status=EventStatus.ESCALATED, escalation=EscalationLevel.IMMEDIATE),
    ev("demo-004", "Airport ground disruption causes cascading schedule changes", "Operational constraints at a regional airport are creating flight delays and potential employee-travel impact.", EventCategory.TRANSPORT, 8, "India", "Delhi NCR", 28.5562, 77.1000, 3, 0.78, 3, ["aviation", "travel", "operations"]),
    ev("demo-005", "Localized public-safety incident triggers access restrictions", "Authorities establish temporary cordons after a public-safety incident near a commercial district; no impact to the demo asset is confirmed.", EventCategory.CRIME_PUBLIC_SAFETY, 1, "India", "Noida", 28.5700, 77.3550, 3, 0.62, 3, ["public-safety", "access", "verification"]),
    ev("demo-006", "Regional telecom outage affects mobile connectivity", "A telecommunications disruption is degrading mobile data and voice services across parts of a metropolitan area.", EventCategory.INFRASTRUCTURE, 3, "India", "Bengaluru", 12.9900, 77.6100, 4, 0.82, 4, ["telecom", "infrastructure", "continuity"], status=EventStatus.MONITORING, escalation=EscalationLevel.WATCH),
    ev("demo-007", "Earthquake reported with limited regional shaking", "A moderate seismic event has been detected; initial reporting indicates limited disruption and no confirmed impact to demo assets.", EventCategory.NATURAL_DISASTER, 11, "India", "Northern India", 30.7333, 76.7794, 2, 0.96, 2, ["earthquake", "natural-hazard"]),
    ev("demo-008", "Security forces increase presence after threat reporting", "Public reporting indicates an elevated security posture around a major transit corridor while authorities assess an unspecified threat.", EventCategory.TERRORISM_CONFLICT, 6, "India", "Delhi NCR", 28.6139, 77.2090, 4, 0.58, 4, ["security", "threat", "transport"], status=EventStatus.REVIEWING, escalation=EscalationLevel.MANAGER_REVIEW),
]

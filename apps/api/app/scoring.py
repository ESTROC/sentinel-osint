from __future__ import annotations

from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
from .models import Asset, PriorityLabel, SecurityEvent


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return radius * 2 * asin(sqrt(a))


def nearest_asset(event: SecurityEvent, assets: list[Asset]) -> tuple[Asset | None, float | None]:
    if event.latitude is None or event.longitude is None or not assets:
        return None, None
    distances = [(asset, haversine_km(event.latitude, event.longitude, asset.latitude, asset.longitude)) for asset in assets]
    return min(distances, key=lambda item: item[1])


def recency_factor(event_time: datetime) -> float:
    now = datetime.now(timezone.utc)
    ts = event_time if event_time.tzinfo else event_time.replace(tzinfo=timezone.utc)
    hours = max((now - ts).total_seconds() / 3600, 0)
    if hours <= 6:
        return 1.0
    if hours <= 24:
        return 0.9
    if hours <= 72:
        return 0.78
    if hours <= 168:
        return 0.66
    return 0.55


def proximity_factor(distance_km: float | None, criticality: int | None) -> float:
    if distance_km is None:
        return 0.75
    crit = criticality or 3
    if distance_km <= 10:
        base = 1.35
    elif distance_km <= 50:
        base = 1.2
    elif distance_km <= 200:
        base = 1.05
    elif distance_km <= 500:
        base = 0.9
    else:
        base = 0.72
    return base * (0.85 + (crit / 5) * 0.3)


def label_for_score(score: float) -> PriorityLabel:
    if score >= 80:
        return PriorityLabel.CRITICAL
    if score >= 60:
        return PriorityLabel.HIGH
    if score >= 35:
        return PriorityLabel.MEDIUM
    return PriorityLabel.LOW


def score_event(event: SecurityEvent, assets: list[Asset]) -> SecurityEvent:
    asset, distance = nearest_asset(event, assets)
    proximity = proximity_factor(distance, asset.criticality if asset else None)
    raw = (
        event.severity * 0.30
        + event.impact * 0.25
        + (event.confidence * 5) * 0.20
        + (recency_factor(event.event_time) * 5) * 0.15
        + (min(proximity, 1.5) / 1.5 * 5) * 0.10
    )
    score = max(0.0, min(100.0, raw / 5 * 100))
    event.priority_score = round(score, 1)
    event.priority = label_for_score(score)
    event.distance_km = round(distance, 1) if distance is not None else None
    if asset:
        event.nearest_asset_id = asset.id
        event.nearest_asset_name = asset.name
    return event

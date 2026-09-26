from datetime import datetime, timezone
from app.demo_data import DEMO_ASSETS
from app.models import EventCategory, SecurityEvent
from app.scoring import haversine_km, label_for_score, score_event


def test_haversine_zero_distance():
    assert haversine_km(28.4595, 77.0266, 28.4595, 77.0266) == 0


def test_priority_label_thresholds():
    assert label_for_score(81).value == "CRITICAL"
    assert label_for_score(61).value == "HIGH"
    assert label_for_score(40).value == "MEDIUM"
    assert label_for_score(10).value == "LOW"


def test_event_scores_and_assigns_asset():
    event = SecurityEvent(
        id="x", title="Test", summary="Test", category=EventCategory.CIVIL_UNREST,
        event_time=datetime.now(timezone.utc), detected_at=datetime.now(timezone.utc),
        country="India", city="Gurgaon", latitude=28.46, longitude=77.03,
        source_name="Test", source_type="DEMO", severity=5, confidence=0.9, impact=5,
    )
    scored = score_event(event, DEMO_ASSETS)
    assert scored.priority_score > 60
    assert scored.nearest_asset_name == "Demo Gurgaon Operations Center"
    assert scored.distance_km is not None and scored.distance_km < 5

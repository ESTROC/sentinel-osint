from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import re
from xml.etree import ElementTree

import httpx
from dateutil import parser as dateparser

from .config import settings
from .models import EventCategory, SecurityEvent, SourceStatus

SOURCE_CATALOG = [
    SourceStatus(id="usgs", name="USGS Earthquake Hazards Program", description="Authoritative seismic event feed.", endpoint="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson", category_focus=["Natural Disaster"]),
    SourceStatus(id="cisa", name="CISA Known Exploited Vulnerabilities", description="Authoritative catalog of vulnerabilities known to be exploited in the wild.", endpoint="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", category_focus=["Cybersecurity Event"]),
    SourceStatus(id="gdacs", name="GDACS", description="Global disaster alerts and coordination information.", endpoint="https://www.gdacs.org/xml/rss.xml", category_focus=["Natural Disaster", "Infrastructure Disruption"]),
    SourceStatus(id="gdelt", name="GDELT DOC 2.0", description="Open global news discovery feed used for public-source event discovery.", endpoint="https://api.gdeltproject.org/api/v2/doc/doc", category_focus=["Civil Unrest", "Public Safety", "Transport", "Security"]),
]


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"


def _safe_dt(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        dt = dateparser.parse(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def _category_from_text(text: str) -> EventCategory:
    lowered = text.lower()
    if any(k in lowered for k in ["protest", "demonstration", "unrest", "riot"]):
        return EventCategory.CIVIL_UNREST
    if any(k in lowered for k in ["terror", "attack", "conflict", "military", "explosion"]):
        return EventCategory.TERRORISM_CONFLICT
    if any(k in lowered for k in ["airport", "flight", "rail", "transport", "traffic"]):
        return EventCategory.TRANSPORT
    if any(k in lowered for k in ["outage", "power", "telecom", "infrastructure"]):
        return EventCategory.INFRASTRUCTURE
    if any(k in lowered for k in ["earthquake", "flood", "cyclone", "storm", "wildfire", "volcano"]):
        return EventCategory.NATURAL_DISASTER
    return EventCategory.CRIME_PUBLIC_SAFETY


async def fetch_usgs(client: httpx.AsyncClient) -> list[SecurityEvent]:
    url = SOURCE_CATALOG[0].endpoint
    response = await client.get(url)
    response.raise_for_status()
    features = response.json().get("features", [])[: settings.max_live_items_per_source]
    events: list[SecurityEvent] = []
    for item in features:
        props = item.get("properties", {})
        coords = (item.get("geometry") or {}).get("coordinates") or [None, None]
        epoch_ms = props.get("time")
        event_time = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc) if epoch_ms else datetime.now(timezone.utc)
        mag = float(props.get("mag") or 0)
        severity = 5 if mag >= 7 else 4 if mag >= 6 else 3 if mag >= 5 else 2
        title = props.get("title") or "Earthquake event"
        events.append(SecurityEvent(
            id=_stable_id("usgs", str(item.get("id") or title)), title=title,
            summary=f"USGS reported seismic activity. Magnitude {mag:.1f}; significance {props.get('sig','n/a')}; alert {props.get('alert') or 'not issued'}.",
            category=EventCategory.NATURAL_DISASTER, event_time=event_time, detected_at=datetime.now(timezone.utc),
            country="Unknown", city=props.get("place"), latitude=coords[1], longitude=coords[0],
            source_name="USGS Earthquake Hazards Program", source_url=props.get("url"), source_type="OFFICIAL",
            severity=severity, confidence=0.98, impact=max(2, min(5, severity)), tags=["earthquake","usgs","natural-hazard"],
            synthetic=False, metadata={"magnitude": mag, "significance": props.get("sig"), "alert": props.get("alert")},
        ))
    return events


async def fetch_cisa(client: httpx.AsyncClient) -> list[SecurityEvent]:
    url = SOURCE_CATALOG[1].endpoint
    response = await client.get(url)
    response.raise_for_status()
    vulns = response.json().get("vulnerabilities", [])[: settings.max_live_items_per_source]
    events: list[SecurityEvent] = []
    for vuln in vulns:
        cve = vuln.get("cveID", "Unknown CVE")
        due = vuln.get("dueDate")
        events.append(SecurityEvent(
            id=_stable_id("cisa", cve), title=f"{cve}: {vuln.get('vulnerabilityName','Known exploited vulnerability')}",
            summary=(vuln.get("shortDescription") or "CISA lists this vulnerability as known exploited in the wild.")[:700],
            category=EventCategory.CYBER, event_time=_safe_dt(vuln.get("dateAdded")), detected_at=datetime.now(timezone.utc),
            country="Global", city="Online", latitude=None, longitude=None, source_name="CISA Known Exploited Vulnerabilities",
            source_url=f"https://www.cisa.gov/known-exploited-vulnerabilities-catalog?search_api_fulltext={cve}", source_type="OFFICIAL",
            severity=5, confidence=0.99, impact=5, tags=["cyber","cisa-kev",cve.lower()], synthetic=False,
            metadata={"vendor": vuln.get("vendorProject"), "product": vuln.get("product"), "due_date": due, "ransomware_use": vuln.get("knownRansomwareCampaignUse")},
        ))
    return events


async def fetch_gdacs(client: httpx.AsyncClient) -> list[SecurityEvent]:
    url = SOURCE_CATALOG[2].endpoint
    response = await client.get(url)
    response.raise_for_status()
    root = ElementTree.fromstring(response.text)
    items = root.findall(".//item")[: settings.max_live_items_per_source]
    events: list[SecurityEvent] = []
    for item in items:
        title = (item.findtext("title") or "GDACS disaster alert").strip()
        link = (item.findtext("link") or "").strip() or None
        description = re.sub(r"<[^>]+>", " ", item.findtext("description") or "")
        text = " ".join(description.split())[:700]
        pub_date = item.findtext("pubDate")
        events.append(SecurityEvent(
            id=_stable_id("gdacs", link or title), title=title, summary=text or "Global disaster alert from GDACS.",
            category=EventCategory.NATURAL_DISASTER, event_time=_safe_dt(pub_date), detected_at=datetime.now(timezone.utc),
            country="Unknown", city=None, latitude=None, longitude=None, source_name="GDACS", source_url=link,
            source_type="OFFICIAL/INTERGOVERNMENTAL", severity=4, confidence=0.9, impact=4,
            tags=["gdacs","disaster","monitoring"], synthetic=False,
        ))
    return events


async def fetch_gdelt(client: httpx.AsyncClient) -> list[SecurityEvent]:
    url = SOURCE_CATALOG[3].endpoint
    params = {
        "query": "(protest OR unrest OR explosion OR evacuation OR airport OR flood OR attack)",
        "mode": "ArtList",
        "maxrecords": str(settings.max_live_items_per_source),
        "format": "json",
        "sort": "HybridRel",
        "timespan": "24h",
    }
    response = await client.get(url, params=params)
    response.raise_for_status()
    articles = response.json().get("articles", [])[: settings.max_live_items_per_source]
    events: list[SecurityEvent] = []
    for article in articles:
        title = article.get("title") or "Public-source security report"
        article_url = article.get("url")
        source_name = article.get("domain") or "GDELT-discovered source"
        category = _category_from_text(title)
        tone = article.get("tone")
        events.append(SecurityEvent(
            id=_stable_id("gdelt", article_url or title), title=title[:220],
            summary="Public-source item discovered through GDELT. Review the original source before treating the report as verified.",
            category=category, event_time=_safe_dt(article.get("seendate")), detected_at=datetime.now(timezone.utc),
            country=article.get("sourcecountry") or "Unknown", city=None, latitude=None, longitude=None,
            source_name=source_name, source_url=article_url, source_type="OPEN_WEB_DISCOVERY", severity=3,
            confidence=0.45, impact=3, tags=["gdelt","open-source","requires-verification"], synthetic=False,
            metadata={"language": article.get("language"), "tone": tone, "image": article.get("socialimage")},
        ))
    return events


async def collect_sources(source_ids: list[str]) -> tuple[list[SecurityEvent], dict[str, str]]:
    handlers = {"usgs": fetch_usgs, "cisa": fetch_cisa, "gdacs": fetch_gdacs, "gdelt": fetch_gdelt}
    events: list[SecurityEvent] = []
    errors: dict[str, str] = {}
    timeout = httpx.Timeout(settings.source_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": "SentinelOSINT/1.0 defensive-research-demo"}) as client:
        for source_id in source_ids:
            handler = handlers.get(source_id.lower())
            if not handler:
                errors[source_id] = "Unknown source"
                continue
            try:
                events.extend(await handler(client))
            except Exception as exc:
                errors[source_id] = f"{type(exc).__name__}: {exc}"
    return events, errors

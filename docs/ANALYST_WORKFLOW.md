# Analyst Workflow

This document describes the intended defensive workflow demonstrated by SentinelOSINT.

## 1. Collect

The system pulls bounded records from public, lawful feeds. Each record retains a source name, source type, source URL when available, event time, and detection time.

## 2. Normalize

Different feeds are converted into a common `SecurityEvent` schema with category, severity, potential impact, confidence, location, tags, and metadata.

## 3. Assess

A transparent priority score helps order the queue. It combines severity, impact, confidence, recency, and proximity to fictional demo assets.

The score does not verify the underlying claim.

## 4. Corroborate

Analysts can attach evidence to an event. Evidence records preserve:
- source name
- source URL
- capture time
- analyst note
- whether the item corroborates or contradicts the current event record

Open-web discovery should be reviewed against the original article and independent or authoritative reporting before being treated as verified.

## 5. Document

The event record tracks analyst notes, state, escalation level, verification status, and an audit history. The briefing endpoint generates a structured summary separating:
- executive summary
- known facts
- information gaps
- source assessment
- organizational relevance
- recommended analyst action

## 6. Escalate or monitor

The platform supports four escalation levels:
- `NONE`
- `WATCH`
- `MANAGER_REVIEW`
- `IMMEDIATE`

And five queue states:
- `NEW`
- `REVIEWING`
- `MONITORING`
- `ESCALATED`
- `CLOSED`

These states are intentionally explicit so the analyst's decision path is reviewable.

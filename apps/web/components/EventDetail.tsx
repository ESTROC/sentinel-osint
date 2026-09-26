'use client';

import Link from 'next/link';
import { ArrowLeft, CheckCircle2, CircleAlert, Clock3, ExternalLink, FileText, MapPin, Radar, ShieldCheck } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getBrief, getEvent } from '@/lib/api';
import type { IncidentBrief, SecurityEvent } from '@/lib/types';
import { PriorityBadge } from './PriorityBadge';
import { AnalystWorkbench } from './AnalystWorkbench';

export function EventDetail({ id }: { id: string }) {
  const [event, setEvent] = useState<SecurityEvent | null>(null);
  const [brief, setBrief] = useState<IncidentBrief | null>(null);
  const [live, setLive] = useState(false);
  useEffect(() => {
    Promise.all([getEvent(id), getBrief(id)]).then(([e,b]) => { setEvent(e.data); setBrief(b.data); setLive(e.live && b.live); });
  }, [id]);
  if (!event) return <main className="inner detail-page"><div className="panel empty-state"><Radar className="pulse"/><h2>Loading event record…</h2></div></main>;

  return (
    <main className="inner detail-page">
      <Link href="/" className="back-link"><ArrowLeft size={15}/> Back to operations</Link>
      <section className="detail-hero">
        <div>
          <div className="detail-kicker"><PriorityBadge priority={event.priority}/><span>{event.category}</span><span className={live ? 'mini-live' : 'source-pill'}>{live ? 'LIVE API' : 'DEMO FALLBACK'}</span></div>
          <h1>{event.title}</h1>
          <p>{event.summary}</p>
        </div>
        <div className="score-orb"><span>PRIORITY</span><strong>{event.priority_score.toFixed(1)}</strong><small>/ 100</small></div>
      </section>

      <section className="detail-grid">
        <div className="detail-main">
          <div className="panel fact-panel">
            <div className="panel-head"><div><span className="eyebrow">EVENT RECORD</span><h2>Operational context</h2></div></div>
            <div className="fact-grid">
              <div><MapPin size={15}/><span>Location</span><strong>{event.city || 'Unknown'}, {event.country}</strong></div>
              <div><Clock3 size={15}/><span>Status</span><strong>{event.status}</strong></div>
              <div><CircleAlert size={15}/><span>Escalation</span><strong>{event.escalation}</strong></div>
              <div><ShieldCheck size={15}/><span>Confidence</span><strong>{Math.round(event.confidence*100)}%</strong></div>
              <div><Radar size={15}/><span>Nearest demo asset</span><strong>{event.nearest_asset_name || 'No match'}</strong></div>
              <div><CheckCircle2 size={15}/><span>Analyst verification</span><strong>{event.verified ? 'Verified' : 'Pending'}</strong></div>
            </div>
          </div>

          <AnalystWorkbench event={event} live={live} onEventChange={setEvent} />

          {brief && <div className="panel brief-panel">
            <div className="panel-head"><div><span className="eyebrow">ANALYST BRIEF</span><h2>Structured incident assessment</h2></div><FileText size={18}/></div>
            <div className="brief-section"><h3>Executive summary</h3><p>{brief.executive_summary}</p></div>
            <div className="brief-columns">
              <div className="brief-section"><h3>Known facts</h3><ul>{brief.known_facts.map(item=><li key={item}>{item}</li>)}</ul></div>
              <div className="brief-section gaps"><h3>Information gaps</h3><ul>{brief.information_gaps.map(item=><li key={item}>{item}</li>)}</ul></div>
            </div>
            <div className="brief-section"><h3>Source assessment</h3><p>{brief.source_assessment}</p></div>
            <div className="brief-section"><h3>Organizational relevance</h3><p>{brief.organizational_relevance}</p></div>
            <div className="action-box"><strong>Recommended analyst action</strong><p>{brief.analyst_action}</p></div>
          </div>}
        </div>

        <aside className="detail-side">
          <div className="panel source-detail">
            <span className="eyebrow">PRIMARY SOURCE</span><h3>{event.source_name}</h3><p><span>Source type</span>{event.source_type}</p><p><span>Detected</span>{new Date(event.detected_at).toLocaleString()}</p><p><span>Event time</span>{new Date(event.event_time).toLocaleString()}</p>
            {event.source_url && <a href={event.source_url} target="_blank" rel="noreferrer">Open original source <ExternalLink size={14}/></a>}
          </div>
          <div className="panel score-detail"><span className="eyebrow">SCORING FACTORS</span><div className="score-row"><span>Severity</span><b>{event.severity}/5</b></div><div className="score-row"><span>Impact</span><b>{event.impact}/5</b></div><div className="score-row"><span>Confidence</span><b>{Math.round(event.confidence*100)}%</b></div><div className="score-row"><span>Proximity</span><b>{event.distance_km != null ? `${event.distance_km} km` : 'N/A'}</b></div><small>Priority is transparent and deterministic; it is not a claim that an event is true.</small></div>
          <div className="panel tags-panel"><span className="eyebrow">TAGS</span><div>{event.tags.map(tag=><span key={tag}>{tag}</span>)}</div></div>
        </aside>
      </section>
    </main>
  );
}

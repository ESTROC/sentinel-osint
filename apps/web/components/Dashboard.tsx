'use client';

import dynamic from 'next/dynamic';
import { Activity, AlertTriangle, CheckCircle2, Radar, Siren, Waves } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { getAssets, getEvents, getMetrics, getSources } from '@/lib/api';
import type { Asset, Metrics, SecurityEvent, SourceStatus } from '@/lib/types';
import { demoAssets, demoEvents, demoMetrics, demoSources } from '@/lib/demo';
import { EventQueue } from './EventQueue';
import { KpiCard } from './KpiCard';
import { SourceCoverage } from './SourceCoverage';

const OperationsMap = dynamic(() => import('./OperationsMap'), { ssr: false, loading: () => <div className="map-loading"><Radar className="pulse"/> Loading situational map…</div> });

export function Dashboard() {
  const [events, setEvents] = useState<SecurityEvent[]>(demoEvents);
  const [metrics, setMetrics] = useState<Metrics>(demoMetrics);
  const [assets, setAssets] = useState<Asset[]>(demoAssets);
  const [sources, setSources] = useState<SourceStatus[]>(demoSources);
  const [live, setLive] = useState(false);

  useEffect(() => {
    Promise.all([getEvents(), getMetrics(), getAssets(), getSources()]).then(([e,m,a,s]) => {
      setEvents(e.data); setMetrics(m.data); setAssets(a.data); setSources(s.data);
      setLive(e.live && m.live && a.live && s.live);
    });
  }, []);

  const topEvent = useMemo(() => events[0], [events]);
  return (
    <main className="inner main-stack">
      <section className="hero-row">
        <div>
          <span className="eyebrow hero-eyebrow">GLOBAL SECURITY MONITORING</span>
          <h1>Situational awareness for fast, defensible decisions.</h1>
          <p>SentinelOSINT aggregates public-source security signals, scores organizational relevance, and gives analysts a structured workflow to review, document, monitor, and escalate emerging events.</p>
        </div>
        <div className="environment-card">
          <span className={live ? 'live-beacon' : 'demo-beacon'}><i/>{live ? 'LIVE API CONNECTED' : 'PORTFOLIO DEMO MODE'}</span>
          <strong>{live ? 'Public-source feeds available through the API' : 'Synthetic scenarios keep the interface reproducible and safe'}</strong>
          <small>Real events are clearly distinguished from synthetic scenarios. Open-web discovery is never treated as verified by default.</small>
        </div>
      </section>

      <section className="kpi-grid">
        <KpiCard label="Monitored events" value={metrics.total_events} helper={`${metrics.source_count} source families`} icon={Radar} />
        <KpiCard label="Critical / high" value={metrics.critical_events + metrics.high_events} helper="Require prioritized review" icon={Siren} tone="danger" />
        <KpiCard label="Under monitoring" value={metrics.monitoring_events} helper="Active watch state" icon={Waves} tone="warning" />
        <KpiCard label="Escalated" value={metrics.escalated_events} helper="Raised for higher review" icon={AlertTriangle} tone="warning" />
        <KpiCard label="Verified" value={metrics.verified_events} helper="Analyst-confirmed records" icon={CheckCircle2} tone="success" />
        <KpiCard label="Synthetic" value={metrics.synthetic_events} helper="Clearly labeled demo cases" icon={Activity} />
      </section>

      <section className="dashboard-grid">
        <div className="panel map-panel">
          <div className="panel-head"><div><span className="eyebrow">SITUATIONAL MAP</span><h2>Events and demo assets</h2></div>{topEvent && <span className="top-signal">Top signal: {topEvent.priority} · {topEvent.priority_score.toFixed(1)}</span>}</div>
          <OperationsMap events={events} assets={assets} />
        </div>
        <aside className="panel doctrine-panel">
          <span className="eyebrow">ANALYTIC DOCTRINE</span>
          <h2>Separate signal from certainty.</h2>
          <p>Source authority, event severity, organizational proximity, corroboration, and analyst verification are treated as distinct concepts.</p>
          <ol className="workflow-list">
            <li><span>01</span><div><strong>Collect</strong><small>Public, lawful sources only</small></div></li>
            <li><span>02</span><div><strong>Assess</strong><small>Severity, confidence, proximity</small></div></li>
            <li><span>03</span><div><strong>Corroborate</strong><small>Preserve source and context</small></div></li>
            <li><span>04</span><div><strong>Document</strong><small>Facts, gaps, analyst notes</small></div></li>
            <li><span>05</span><div><strong>Escalate</strong><small>Only when thresholds are met</small></div></li>
          </ol>
        </aside>
      </section>

      <EventQueue events={events} />
      <SourceCoverage sources={sources} />
    </main>
  );
}

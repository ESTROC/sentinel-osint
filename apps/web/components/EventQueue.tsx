'use client';

import Link from 'next/link';
import { ArrowUpRight, CheckCircle2, Clock3, Search } from 'lucide-react';
import { useMemo, useState } from 'react';
import { PriorityBadge } from './PriorityBadge';
import type { SecurityEvent } from '@/lib/types';

function timeAgo(value: string) {
  const minutes = Math.max(1, Math.round((Date.now() - new Date(value).getTime()) / 60000));
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

export function EventQueue({ events }: { events: SecurityEvent[] }) {
  const [query, setQuery] = useState('');
  const [priority, setPriority] = useState('ALL');
  const filtered = useMemo(() => events.filter(event => {
    const matchesQuery = `${event.title} ${event.category} ${event.country} ${event.city || ''}`.toLowerCase().includes(query.toLowerCase());
    const matchesPriority = priority === 'ALL' || event.priority === priority;
    return matchesQuery && matchesPriority;
  }), [events, query, priority]);

  return (
    <section className="panel event-panel">
      <div className="panel-head queue-head">
        <div><span className="eyebrow">ANALYST QUEUE</span><h2>Priority incidents</h2></div>
        <div className="queue-tools">
          <label className="search"><Search size={14}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search events" /></label>
          <select value={priority} onChange={e=>setPriority(e.target.value)} aria-label="Filter by priority">
            <option value="ALL">All priorities</option><option>CRITICAL</option><option>HIGH</option><option>MEDIUM</option><option>LOW</option>
          </select>
        </div>
      </div>
      <div className="table-wrap">
        <table className="event-table">
          <thead><tr><th>Priority</th><th>Event</th><th>Location</th><th>Source</th><th>Status</th><th>Detected</th><th></th></tr></thead>
          <tbody>
            {filtered.map(event => (
              <tr key={event.id}>
                <td><PriorityBadge priority={event.priority} /></td>
                <td className="event-title-cell"><strong>{event.title}</strong><span>{event.category} · Score {event.priority_score.toFixed(1)}</span></td>
                <td>{event.city || event.country}<span className="subtle">{event.nearest_asset_name ? `${event.distance_km ?? '—'} km to asset` : 'No asset match'}</span></td>
                <td><span className="source-pill">{event.source_type}</span><span className="subtle">{event.source_name}</span></td>
                <td><span className="status"><Clock3 size={13}/>{event.status}</span>{event.verified && <span className="verified"><CheckCircle2 size={12}/> Verified</span>}</td>
                <td>{timeAgo(event.detected_at)}</td>
                <td><Link className="row-link" href={`/events/${event.id}`} aria-label={`Open ${event.title}`}><ArrowUpRight size={16}/></Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

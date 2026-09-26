import { demoAssets, demoEvents, demoMetrics, demoSources } from './demo';
import type { Asset, IncidentBrief, Metrics, SecurityEvent, SourceStatus } from './types';

export const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || '').replace(/\/$/, '');

async function request<T>(path: string, fallback: T): Promise<{ data: T; live: boolean }> {
  if (!API_BASE) return { data: fallback, live: false };
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`API ${response.status}`);
    return { data: await response.json() as T, live: true };
  } catch {
    return { data: fallback, live: false };
  }
}

export const getEvents = () => request<SecurityEvent[]>('/api/events', demoEvents);
export const getMetrics = () => request<Metrics>('/api/metrics', demoMetrics);
export const getAssets = () => request<Asset[]>('/api/assets', demoAssets);
export const getSources = () => request<SourceStatus[]>('/api/sources', demoSources);

export async function getEvent(id: string): Promise<{ data: SecurityEvent | null; live: boolean }> {
  const fallback = demoEvents.find(event => event.id === id) || null;
  return request<SecurityEvent | null>(`/api/events/${id}`, fallback);
}

export async function getBrief(id: string): Promise<{ data: IncidentBrief | null; live: boolean }> {
  const event = demoEvents.find(item => item.id === id);
  const fallback: IncidentBrief | null = event ? {
    event_id: event.id,
    generated_at: new Date().toISOString(),
    title: event.title,
    executive_summary: event.summary,
    known_facts: [
      `Event category: ${event.category}.`,
      `Reported location: ${event.city || 'Unknown'}, ${event.country}.`,
      `Analyst priority: ${event.priority} (${event.priority_score.toFixed(1)}/100).`,
      `Primary source: ${event.source_name}.`,
    ],
    information_gaps: ['Synthetic demonstration record. Validate against real primary and independent sources before operational use.'],
    source_assessment: `Current scenario confidence is ${(event.confidence * 100).toFixed(0)}%. This synthetic record demonstrates the analysis workflow only.`,
    organizational_relevance: event.nearest_asset_name ? `${event.nearest_asset_name} is approximately ${event.distance_km ?? 'n/a'} km from the scenario location.` : 'No asset proximity available.',
    analyst_action: 'Continue monitoring, corroborate material details, and escalate only when verified information meets the defined threshold.',
    source_links: [],
  } : null;
  return request<IncidentBrief | null>(`/api/events/${id}/brief`, fallback);
}

export async function updateEvent(id: string, patch: Record<string, unknown>): Promise<SecurityEvent> {
  if (!API_BASE) throw new Error('Live API is not configured');
  const response = await fetch(`${API_BASE}/api/events/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  });
  if (!response.ok) throw new Error(`Update failed (${response.status})`);
  return response.json();
}

export async function addEvidence(id: string, payload: Record<string, unknown>) {
  if (!API_BASE) throw new Error('Live API is not configured');
  const response = await fetch(`${API_BASE}/api/events/${id}/evidence`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`Evidence update failed (${response.status})`);
  return response.json();
}

export async function getEvidence(id: string) {
  return request<import('./types').Evidence[]>(`/api/events/${id}/evidence`, []);
}

export async function getAudit(id: string) {
  return request<import('./types').AuditRecord[]>(`/api/events/${id}/audit`, []);
}

export async function ingestLiveSources(sources = ['usgs', 'cisa', 'gdacs', 'gdelt']) {
  if (!API_BASE) throw new Error('Live API is not configured');
  const response = await fetch(`${API_BASE}/api/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sources, actor: 'portfolio-analyst' }),
  });
  if (!response.ok) throw new Error(`Ingestion failed (${response.status})`);
  return response.json() as Promise<{ ingested: number; errors: Record<string, string>; sources_requested: string[] }>;
}

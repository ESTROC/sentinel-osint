export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type EventStatus = 'NEW' | 'REVIEWING' | 'MONITORING' | 'ESCALATED' | 'CLOSED';
export type Escalation = 'NONE' | 'WATCH' | 'MANAGER_REVIEW' | 'IMMEDIATE';

export interface SecurityEvent {
  id: string; title: string; summary: string; category: string; event_time: string; detected_at: string;
  country: string; city?: string | null; latitude?: number | null; longitude?: number | null;
  source_name: string; source_url?: string | null; source_type: string; severity: number; confidence: number; impact: number;
  status: EventStatus; escalation: Escalation; analyst_notes: string; verified: boolean;
  nearest_asset_id?: string | null; nearest_asset_name?: string | null; distance_km?: number | null;
  priority_score: number; priority: Priority; tags: string[]; synthetic: boolean; metadata: Record<string, unknown>;
}

export interface Metrics {
  total_events: number; critical_events: number; high_events: number; escalated_events: number;
  monitoring_events: number; verified_events: number; synthetic_events: number; source_count: number;
  category_breakdown: Record<string, number>;
}

export interface Asset {
  id: string; name: string; city: string; country: string; latitude: number; longitude: number;
  criticality: number; asset_type: string;
}

export interface IncidentBrief {
  event_id: string; generated_at: string; title: string; executive_summary: string;
  known_facts: string[]; information_gaps: string[]; source_assessment: string;
  organizational_relevance: string; analyst_action: string; source_links: string[];
}

export interface SourceStatus {
  id: string; name: string; description: string; endpoint: string; category_focus: string[];
  enabled: boolean; live_supported: boolean;
}

export interface Evidence {
  id: string; event_id: string; source_name: string; source_url?: string | null;
  captured_at: string; note: string; corroborates: boolean;
}

export interface AuditRecord {
  id: string; event_id: string; timestamp: string; actor: string; action: string; detail: string;
}

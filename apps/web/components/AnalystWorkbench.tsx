'use client';

import { CheckCircle2, ClipboardCheck, Link2, Loader2, Save, ShieldAlert } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { addEvidence, getAudit, getEvidence, updateEvent } from '@/lib/api';
import type { AuditRecord, Escalation, EventStatus, Evidence, SecurityEvent } from '@/lib/types';

export function AnalystWorkbench({ event, live, onEventChange }: { event: SecurityEvent; live: boolean; onEventChange: (event: SecurityEvent) => void }) {
  const [status, setStatus] = useState<EventStatus>(event.status);
  const [escalation, setEscalation] = useState<Escalation>(event.escalation);
  const [notes, setNotes] = useState(event.analyst_notes || '');
  const [verified, setVerified] = useState(event.verified);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [audit, setAudit] = useState<AuditRecord[]>([]);
  const [sourceName, setSourceName] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [evidenceNote, setEvidenceNote] = useState('');
  const [corroborates, setCorroborates] = useState(true);

  const canWrite = live;
  useEffect(() => {
    if (!live) return;
    Promise.all([getEvidence(event.id), getAudit(event.id)]).then(([e,a]) => { setEvidence(e.data); setAudit(a.data); });
  }, [event.id, live]);

  const changed = useMemo(() => status !== event.status || escalation !== event.escalation || notes !== (event.analyst_notes || '') || verified !== event.verified, [status, escalation, notes, verified, event]);

  async function save() {
    if (!canWrite || !changed) return;
    setSaving(true); setMessage('');
    try {
      const updated = await updateEvent(event.id, { status, escalation, analyst_notes: notes, verified, actor: 'portfolio-analyst' });
      onEventChange(updated);
      const a = await getAudit(event.id); setAudit(a.data);
      setMessage('Analyst record saved.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Update failed'); }
    finally { setSaving(false); }
  }

  async function submitEvidence() {
    if (!canWrite || !sourceName.trim()) return;
    setSaving(true); setMessage('');
    try {
      await addEvidence(event.id, { source_name: sourceName, source_url: sourceUrl || null, note: evidenceNote, corroborates, actor: 'portfolio-analyst' });
      const [e,a] = await Promise.all([getEvidence(event.id), getAudit(event.id)]); setEvidence(e.data); setAudit(a.data);
      setSourceName(''); setSourceUrl(''); setEvidenceNote('');
      setMessage('Evidence record added.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Evidence update failed'); }
    finally { setSaving(false); }
  }

  return <div className="panel workbench-panel">
    <div className="panel-head"><div><span className="eyebrow">ANALYST WORKBENCH</span><h2>Review, corroborate, document</h2></div><span className={canWrite ? 'mini-live' : 'source-pill'}>{canWrite ? 'API WRITE MODE' : 'READ-ONLY FALLBACK'}</span></div>
    <div className="workbench-body">
      <div className="triage-grid">
        <label><span>Status</span><select value={status} onChange={e=>setStatus(e.target.value as EventStatus)} disabled={!canWrite}><option>NEW</option><option>REVIEWING</option><option>MONITORING</option><option>ESCALATED</option><option>CLOSED</option></select></label>
        <label><span>Escalation</span><select value={escalation} onChange={e=>setEscalation(e.target.value as Escalation)} disabled={!canWrite}><option>NONE</option><option>WATCH</option><option>MANAGER_REVIEW</option><option>IMMEDIATE</option></select></label>
        <label className="verify-check"><input type="checkbox" checked={verified} onChange={e=>setVerified(e.target.checked)} disabled={!canWrite}/><CheckCircle2 size={15}/><span>Analyst verified</span></label>
      </div>
      <label className="notes-field"><span>Analyst notes</span><textarea value={notes} onChange={e=>setNotes(e.target.value)} disabled={!canWrite} placeholder="Record factual observations, uncertainties, and action taken." rows={4}/></label>
      <button className="primary-button" onClick={save} disabled={!canWrite || !changed || saving}>{saving ? <Loader2 size={15} className="spin"/> : <Save size={15}/>} Save analyst record</button>
      {message && <p className="workbench-message">{message}</p>}

      <div className="workbench-divider"/>
      <div className="evidence-form">
        <div><span className="eyebrow">CORROBORATING EVIDENCE</span><h3>Attach a source record</h3></div>
        <div className="evidence-fields">
          <label><span>Source name</span><input value={sourceName} onChange={e=>setSourceName(e.target.value)} disabled={!canWrite} placeholder="Official agency / publication"/></label>
          <label><span>Source URL</span><input value={sourceUrl} onChange={e=>setSourceUrl(e.target.value)} disabled={!canWrite} placeholder="https://…"/></label>
          <label className="wide"><span>Analyst note</span><input value={evidenceNote} onChange={e=>setEvidenceNote(e.target.value)} disabled={!canWrite} placeholder="What does this source add or contradict?"/></label>
          <label className="verify-check"><input type="checkbox" checked={corroborates} onChange={e=>setCorroborates(e.target.checked)} disabled={!canWrite}/><ClipboardCheck size={15}/><span>Corroborates current record</span></label>
        </div>
        <button className="secondary-button" onClick={submitEvidence} disabled={!canWrite || !sourceName.trim() || saving}><Link2 size={14}/> Add evidence</button>
      </div>

      {(evidence.length > 0 || audit.length > 0) && <div className="evidence-audit-grid">
        <div><h3>Evidence ledger</h3>{evidence.length ? evidence.map(item=><div className="ledger-item" key={item.id}><span className={item.corroborates ? 'ledger-ok' : 'ledger-warn'}>{item.corroborates ? 'CORROBORATES' : 'CONTRADICTS'}</span><strong>{item.source_name}</strong><small>{item.note || 'No note'} · {new Date(item.captured_at).toLocaleString()}</small></div>) : <p className="empty-copy">No evidence attached.</p>}</div>
        <div><h3>Audit trail</h3>{audit.length ? audit.slice().reverse().map(item=><div className="ledger-item" key={item.id}><span className="ledger-action">{item.action}</span><strong>{item.actor}</strong><small>{item.detail} · {new Date(item.timestamp).toLocaleString()}</small></div>) : <p className="empty-copy">No analyst actions recorded.</p>}</div>
      </div>}
      {!canWrite && <div className="readonly-note"><ShieldAlert size={15}/><span>Connect the deployed API to enable persistent triage, evidence, and audit actions.</span></div>}
    </div>
  </div>;
}

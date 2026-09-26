import { CheckCircle2, Database, Eye, FileWarning, Scale, ShieldCheck } from 'lucide-react';

export default function MethodologyPage() {
  const principles = [
    [Database, 'Collect lawfully', 'Use public, attributable feeds and open-web discovery sources. Private accounts, credentials, bypass techniques, and covert collection are out of scope.'],
    [Eye, 'Discovery is not verification', 'A news item discovered through an aggregator remains unverified until the original source and corroborating evidence are assessed.'],
    [Scale, 'Score transparently', 'Priority is calculated from severity, potential impact, confidence, recency, and proximity to fictional demo assets. Weights are documented in code.'],
    [FileWarning, 'Preserve uncertainty', 'Incident briefs state known facts and information gaps separately so assumptions are not promoted into facts.'],
    [CheckCircle2, 'Keep humans in the loop', 'Analyst verification and escalation are explicit actions. The platform does not silently auto-verify public reporting.'],
    [ShieldCheck, 'Minimize harm', 'The project is designed for defensive situational awareness and portfolio demonstration, not monitoring private individuals.'],
  ] as const;
  return <main className="inner methodology-page"><section className="method-hero"><span className="eyebrow">METHODOLOGY & ETHICS</span><h1>Useful intelligence requires disciplined uncertainty.</h1><p>SentinelOSINT is designed around a simple principle: an event can be important before it is fully verified, but the interface must never confuse relevance with truth.</p></section><section className="method-grid">{principles.map(([Icon,title,body])=><article className="panel method-card" key={title}><span><Icon size={18}/></span><h2>{title}</h2><p>{body}</p></article>)}</section><section className="panel formula-panel"><span className="eyebrow">PRIORITY MODEL</span><h2>Deterministic, explainable scoring</h2><code>priority = 30% severity + 25% impact + 20% confidence + 15% recency + 10% proximity</code><p>The score orders the analyst queue. It does not prove that a claim is accurate. Confidence and analyst verification remain separate fields.</p></section><section className="panel workflow-panel"><span className="eyebrow">ANALYST WORKFLOW</span><div className="workflow-strip"><b>Collect</b><i>→</i><b>Normalize</b><i>→</i><b>Assess</b><i>→</i><b>Corroborate</b><i>→</i><b>Document</b><i>→</i><b>Escalate / Monitor</b></div></section></main>;
}

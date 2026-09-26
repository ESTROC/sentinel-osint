import { DatabaseZap, Globe2, RadioTower, ShieldAlert } from 'lucide-react';
import type { SourceStatus } from '@/lib/types';

const icons = [Globe2, ShieldAlert, RadioTower, DatabaseZap];

export function SourceCoverage({ sources }: { sources: SourceStatus[] }) {
  return (
    <section className="panel source-panel">
      <div className="panel-head"><div><span className="eyebrow">SOURCE COVERAGE</span><h2>Public-source collection</h2></div><span className="mini-live"><i/> {sources.length} connected</span></div>
      <div className="source-grid">
        {sources.map((source, index) => {
          const Icon = icons[index % icons.length];
          return <div className="source-card" key={source.id}><span className="source-icon"><Icon size={17}/></span><div><strong>{source.name}</strong><p>{source.description}</p><small>{source.category_focus.join(' · ')}</small></div></div>;
        })}
      </div>
    </section>
  );
}

import type { LucideIcon } from 'lucide-react';

export function KpiCard({ label, value, helper, icon: Icon, tone = 'default' }: { label: string; value: string | number; helper: string; icon: LucideIcon; tone?: 'default' | 'danger' | 'warning' | 'success' }) {
  return (
    <div className={`kpi-card kpi-${tone}`}>
      <div className="kpi-icon"><Icon size={17} strokeWidth={1.8} /></div>
      <div>
        <div className="kpi-label">{label}</div>
        <div className="kpi-value">{value}</div>
        <div className="kpi-helper">{helper}</div>
      </div>
    </div>
  );
}

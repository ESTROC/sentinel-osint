import Link from 'next/link';
import { Github, Radar, ShieldCheck } from 'lucide-react';

export function NavBar() {
  return (
    <header className="nav-shell">
      <nav className="nav inner">
        <Link href="/" className="brand">
          <span className="brand-mark"><Radar size={18} /></span>
          <span><strong>SentinelOSINT</strong><small>Security Intelligence Workbench</small></span>
        </Link>
        <div className="nav-links">
          <Link href="/">Operations</Link>
          <Link href="/methodology">Methodology</Link>
          <a href="https://github.com/ESTROC/sentinel-osint" target="_blank" rel="noreferrer"><Github size={15} /> GitHub</a>
        </div>
        <div className="trust-chip"><ShieldCheck size={14} /><span>Defensive OSINT</span></div>
      </nav>
    </header>
  );
}

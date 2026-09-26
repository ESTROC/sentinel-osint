import type { Metadata } from 'next';
import 'leaflet/dist/leaflet.css';
import './globals.css';
import { NavBar } from '@/components/NavBar';

export const metadata: Metadata = {
  title: 'SentinelOSINT | Security Intelligence Workbench',
  description: 'Defensive open-source security event monitoring, situational awareness, triage, and incident briefing.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><NavBar />{children}<footer className="footer inner"><div><strong>SentinelOSINT</strong><span>Defensive OSINT portfolio project</span></div><p>Public-source research only. Synthetic scenarios are explicitly labeled. No private-person targeting or covert collection.</p></footer></body></html>;
}

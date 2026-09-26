'use client';

import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet';
import type { Asset, SecurityEvent } from '@/lib/types';

const priorityColor: Record<string, string> = {
  CRITICAL: '#ef476f',
  HIGH: '#ff9f43',
  MEDIUM: '#ffd166',
  LOW: '#48cae4',
};

export default function OperationsMap({ events, assets }: { events: SecurityEvent[]; assets: Asset[] }) {
  const geoEvents = events.filter(event => typeof event.latitude === 'number' && typeof event.longitude === 'number');
  return (
    <div className="map-wrap">
      <MapContainer center={[22.8, 78.9]} zoom={4} scrollWheelZoom={false} className="map-canvas" zoomControl={true}>
        <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {geoEvents.map(event => (
          <CircleMarker key={event.id} center={[event.latitude!, event.longitude!]} radius={event.priority === 'CRITICAL' ? 10 : 7} pathOptions={{ color: priorityColor[event.priority], fillColor: priorityColor[event.priority], fillOpacity: .82, weight: 2 }}>
            <Popup>
              <strong>{event.title}</strong><br />
              {event.city || event.country}<br />
              Priority: {event.priority} · Score {event.priority_score.toFixed(1)}
            </Popup>
          </CircleMarker>
        ))}
        {assets.map(asset => (
          <CircleMarker key={asset.id} center={[asset.latitude, asset.longitude]} radius={5} pathOptions={{ color: '#6ae4ff', fillColor: '#082c3c', fillOpacity: 1, weight: 2 }}>
            <Popup><strong>{asset.name}</strong><br />{asset.asset_type} · Criticality {asset.criticality}/5</Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <div className="map-legend">
        <span><i className="dot critical" /> Critical</span><span><i className="dot high" /> High</span><span><i className="dot medium" /> Medium</span><span><i className="dot asset" /> Demo asset</span>
      </div>
    </div>
  );
}

import type { Asset, Metrics, SecurityEvent, SourceStatus } from './types';

const now = Date.now();
const ago = (hours: number) => new Date(now - hours * 3600_000).toISOString();

export const demoAssets: Asset[] = [
  { id: 'asset-gurgaon', name: 'Demo Gurgaon Operations Center', city: 'Gurgaon', country: 'India', latitude: 28.4595, longitude: 77.0266, criticality: 5, asset_type: 'Operations Center' },
  { id: 'asset-noida', name: 'Demo Noida Technology Hub', city: 'Noida', country: 'India', latitude: 28.5355, longitude: 77.3910, criticality: 4, asset_type: 'Technology Hub' },
  { id: 'asset-hyderabad', name: 'Demo Hyderabad Delivery Center', city: 'Hyderabad', country: 'India', latitude: 17.385, longitude: 78.4867, criticality: 4, asset_type: 'Delivery Center' },
  { id: 'asset-bengaluru', name: 'Demo Bengaluru Engineering Hub', city: 'Bengaluru', country: 'India', latitude: 12.9716, longitude: 77.5946, criticality: 4, asset_type: 'Engineering Hub' },
];

export const demoEvents: SecurityEvent[] = [
  { id:'demo-003', title:'Critical vulnerability added to active exploitation watchlist', summary:'A newly tracked vulnerability affecting a common enterprise component is being reviewed for potential relevance to the demo technology estate.', category:'Cybersecurity Event', event_time:ago(5), detected_at:ago(4), country:'Global', city:'Online', latitude:28.5355, longitude:77.391, source_name:'Synthetic Scenario Feed', source_type:'DEMO', severity:5, confidence:.95, impact:5, status:'ESCALATED', escalation:'IMMEDIATE', analyst_notes:'', verified:false, nearest_asset_id:'asset-noida', nearest_asset_name:'Demo Noida Technology Hub', distance_km:0, priority_score:91.5, priority:'CRITICAL', tags:['cyber','vulnerability','kev'], synthetic:true, metadata:{scenario:true}},
  { id:'demo-001', title:'Civil unrest disrupts arterial routes near business district', summary:'Large demonstrations and temporary road closures create employee-travel and access concerns near a fictional corporate operating area.', category:'Civil Unrest', event_time:ago(2), detected_at:ago(1), country:'India', city:'Gurgaon', latitude:28.472, longitude:77.061, source_name:'Synthetic Scenario Feed', source_type:'DEMO', severity:4, confidence:.86, impact:4, status:'REVIEWING', escalation:'MANAGER_REVIEW', analyst_notes:'', verified:false, nearest_asset_id:'asset-gurgaon', nearest_asset_name:'Demo Gurgaon Operations Center', distance_km:3.7, priority_score:78.2, priority:'HIGH', tags:['civil-unrest','travel','access'], synthetic:true, metadata:{scenario:true}},
  { id:'demo-006', title:'Regional telecom outage affects mobile connectivity', summary:'A telecommunications disruption is degrading mobile data and voice services across parts of a metropolitan area.', category:'Infrastructure Disruption', event_time:ago(3), detected_at:ago(2), country:'India', city:'Bengaluru', latitude:12.99, longitude:77.61, source_name:'Synthetic Scenario Feed', source_type:'DEMO', severity:4, confidence:.82, impact:4, status:'MONITORING', escalation:'WATCH', analyst_notes:'', verified:false, nearest_asset_id:'asset-bengaluru', nearest_asset_name:'Demo Bengaluru Engineering Hub', distance_km:2.6, priority_score:75.9, priority:'HIGH', tags:['telecom','infrastructure','continuity'], synthetic:true, metadata:{scenario:true}},
  { id:'demo-002', title:'Severe weather produces localized flooding and transport delays', summary:'Heavy rainfall is causing waterlogging, traffic disruption, and intermittent access constraints near a fictional delivery center.', category:'Natural Disaster', event_time:ago(4), detected_at:ago(3), country:'India', city:'Hyderabad', latitude:17.41, longitude:78.47, source_name:'Synthetic Scenario Feed', source_type:'DEMO', severity:3, confidence:.91, impact:4, status:'MONITORING', escalation:'WATCH', analyst_notes:'', verified:false, nearest_asset_id:'asset-hyderabad', nearest_asset_name:'Demo Hyderabad Delivery Center', distance_km:3.3, priority_score:69.4, priority:'HIGH', tags:['flood','weather','transport'], synthetic:true, metadata:{scenario:true}},
  { id:'demo-008', title:'Security forces increase presence after threat reporting', summary:'Public reporting indicates an elevated security posture around a major transit corridor while authorities assess an unspecified threat.', category:'Terrorism / Armed Conflict', event_time:ago(6), detected_at:ago(5), country:'India', city:'Delhi NCR', latitude:28.6139, longitude:77.209, source_name:'Synthetic Scenario Feed', source_type:'DEMO', severity:4, confidence:.58, impact:4, status:'REVIEWING', escalation:'MANAGER_REVIEW', analyst_notes:'', verified:false, nearest_asset_id:'asset-noida', nearest_asset_name:'Demo Noida Technology Hub', distance_km:20.5, priority_score:66.7, priority:'HIGH', tags:['security','threat','transport'], synthetic:true, metadata:{scenario:true}},
  { id:'demo-005', title:'Localized public-safety incident triggers access restrictions', summary:'Authorities establish temporary cordons after a public-safety incident near a commercial district; no impact to the demo asset is confirmed.', category:'Crime / Public Safety', event_time:ago(1), detected_at:ago(1), country:'India', city:'Noida', latitude:28.57, longitude:77.355, source_name:'Synthetic Scenario Feed', source_type:'DEMO', severity:3, confidence:.62, impact:3, status:'NEW', escalation:'NONE', analyst_notes:'', verified:false, nearest_asset_id:'asset-noida', nearest_asset_name:'Demo Noida Technology Hub', distance_km:5.5, priority_score:58.3, priority:'MEDIUM', tags:['public-safety','access','verification'], synthetic:true, metadata:{scenario:true}},
];

export const demoSources: SourceStatus[] = [
  { id:'usgs', name:'USGS Earthquake Hazards Program', description:'Authoritative seismic event feed.', endpoint:'https://earthquake.usgs.gov/', category_focus:['Natural Disaster'], enabled:true, live_supported:true },
  { id:'cisa', name:'CISA Known Exploited Vulnerabilities', description:'Authoritative actively exploited vulnerability catalog.', endpoint:'https://www.cisa.gov/known-exploited-vulnerabilities-catalog', category_focus:['Cybersecurity Event'], enabled:true, live_supported:true },
  { id:'gdacs', name:'GDACS', description:'Global disaster alerts and coordination information.', endpoint:'https://www.gdacs.org/', category_focus:['Natural Disaster'], enabled:true, live_supported:true },
  { id:'gdelt', name:'GDELT DOC 2.0', description:'Open global-news discovery for public-source monitoring.', endpoint:'https://www.gdeltproject.org/', category_focus:['Civil Unrest','Security'], enabled:true, live_supported:true },
];

export const demoMetrics: Metrics = {
  total_events: demoEvents.length,
  critical_events: demoEvents.filter(e=>e.priority==='CRITICAL').length,
  high_events: demoEvents.filter(e=>e.priority==='HIGH').length,
  escalated_events: demoEvents.filter(e=>e.status==='ESCALATED').length,
  monitoring_events: demoEvents.filter(e=>e.status==='MONITORING').length,
  verified_events: 0,
  synthetic_events: demoEvents.length,
  source_count: 4,
  category_breakdown: demoEvents.reduce<Record<string,number>>((acc,e)=>{acc[e.category]=(acc[e.category]||0)+1; return acc;},{}),
};

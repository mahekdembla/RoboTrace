/**
 * Human-in-the-Loop Annotation records according to design.md Section 4.G & 4.I
 * Stores human review decisions, preserving original suggested error labels.
 */

export const MOCK_ANNOTATIONS = [
  {
    id: 'ANN-001',
    error_id: 'ERR-194',
    mission_id: 'MISSION-002',
    agent_id: 'TITAN',
    step_id: 2,
    suggested_category: 'Coordination Error',
    final_category: 'Coordination Error',
    severity: 'Low',
    decision: 'ACCEPTED',
    reviewer_name: 'Lead Robotics Auditor (Sarah Chen)',
    reviewer_feedback: 'Confirmed: Proximity hold was appropriate. Safe spacing maintained with no impact.',
    status: 'REVIEWED',
    timestamp: '2026-11-04 06:45:10'
  },
  {
    id: 'ANN-002',
    error_id: 'ERR-188',
    mission_id: 'MISSION-002',
    agent_id: 'NOVA',
    step_id: 1,
    suggested_category: 'Perception Error',
    final_category: 'Planning Error',
    severity: 'Medium',
    decision: 'CORRECTED',
    reviewer_name: 'Lead Robotics Auditor (Sarah Chen)',
    reviewer_feedback: 'Re-classified from Perception to Planning: Sensor was functioning correctly; the planner selected an obsolete inspection waypoint.',
    status: 'REVIEWED',
    timestamp: '2026-11-04 06:50:22'
  }
];

export const MOCK_WAREHOUSE_ZONES = [
  {
    id: 'zone-racks-west',
    name: 'Storage Racks West (Aisles A & B)',
    category: 'Storage',
    bounds: { minX: -16.0, maxX: -4.0, minZ: -10.0, maxZ: 10.0 },
    color: '#3b82f6'
  },
  {
    id: 'zone-racks-east',
    name: 'High-Bay Racks East (Aisles C & D)',
    category: 'Storage',
    bounds: { minX: 4.0, maxX: 16.0, minZ: -10.0, maxZ: 10.0 },
    color: '#3b82f6'
  },
  {
    id: 'zone-highway',
    name: 'Central Arterial Highway & Crossway',
    category: 'Transit',
    bounds: { minX: -3.0, maxX: 3.0, minZ: -18.0, maxZ: 18.0 },
    color: '#10b981'
  },
  {
    id: 'zone-inspect',
    name: 'Quality Inspection & Scanner Gantry',
    category: 'Inspection',
    bounds: { minX: -3.5, maxX: 3.5, minZ: 7.0, maxZ: 11.5 },
    color: '#8b5cf6'
  },
  {
    id: 'zone-pack',
    name: 'Packing Station & Conveyors',
    category: 'Packing',
    bounds: { minX: -6.0, maxX: 6.0, minZ: 13.0, maxZ: 18.0 },
    color: '#06b6d4'
  },
  {
    id: 'zone-docks',
    name: 'Truck Loading Bays & Charging Docks',
    category: 'Shipping',
    bounds: { minX: -14.0, maxX: 14.0, minZ: -18.0, maxZ: -11.0 },
    color: '#f59e0b'
  }
];

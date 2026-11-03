/**
 * AgentGuard Error Taxonomy and Detected Errors according to design.md Section 4.H
 */

export const ERROR_TAXONOMY = [
  { id: 'Perception Error', name: 'Perception Error', description: 'Robot failed to identify an object, tag, or obstacle.' },
  { id: 'Navigation Error', name: 'Navigation Error', description: 'Robot selected an invalid or blocked route.' },
  { id: 'Planning Error', name: 'Planning Error', description: 'Robot selected an action not appropriate for the assigned task.' },
  { id: 'Manipulation Error', name: 'Manipulation Error', description: 'Robot failed to pick, hold, or place a package.' },
  { id: 'Collision Error', name: 'Collision Error', description: 'Robot collided with a shelf, obstacle, or another robot.' },
  { id: 'Execution Error', name: 'Execution Error', description: 'Robot performed an incorrect movement or mechanical action.' },
  { id: 'Recovery Error', name: 'Recovery Error', description: 'Robot failed to recover or re-plan after an error.' },
  { id: 'Task Completion Error', name: 'Task Completion Error', description: 'Robot reported task completion without achieving expected result.' },
  { id: 'Coordination Error', name: 'Coordination Error', description: 'Multiple agents interfered with each other in shared warehouse zones.' }
];

export const MOCK_INCIDENTS = [
  {
    id: 'ERR-201',
    agent_id: 'ATLAS',
    agentName: 'Atlas',
    mission_id: 'MISSION-001',
    step_id: 3,
    error_category: 'Collision Error',
    suggested_category: 'Collision Error',
    severity: 'High',
    description: 'Chassis collision with Shelf A upright post during lateral avoidance turn.',
    evidence: 'LiDAR range dropped to 0.02m at (x: -8.2, z: -3.2). Motor stall current spiked to 18A.',
    status: 'PENDING_REVIEW',
    timestamp: '08:30:45',
    location: 'Shelf Rack A-2 (Picking Aisle)'
  },
  {
    id: 'ERR-202',
    agent_id: 'ATLAS',
    agentName: 'Atlas',
    mission_id: 'MISSION-001',
    step_id: 4,
    error_category: 'Manipulation Error',
    suggested_category: 'Manipulation Error',
    severity: 'High',
    description: 'Empty gripper closure executed without package engagement.',
    evidence: 'Optical beam unbroken between gripper fingers. Grasp load measured 0.0kg vs expected 8.4kg.',
    status: 'PENDING_REVIEW',
    timestamp: '08:31:02',
    location: 'Shelf Rack A-2 (Picking Aisle)'
  },
  {
    id: 'ERR-203',
    agent_id: 'ATLAS',
    agentName: 'Atlas',
    mission_id: 'MISSION-001',
    step_id: 5,
    error_category: 'Task Completion Error',
    suggested_category: 'Task Completion Error',
    severity: 'Medium',
    description: 'Agent reported delivery success to Station B despite empty payload deck.',
    evidence: 'Delivery station pressure sensor shows 0kg delivered. Task status falsely reported as COMPLETED.',
    status: 'PENDING_REVIEW',
    timestamp: '08:31:25',
    location: 'Station B (Packing Area)'
  },
  {
    id: 'ERR-194',
    agent_id: 'TITAN',
    agentName: 'Titan',
    mission_id: 'MISSION-002',
    step_id: 2,
    error_category: 'Coordination Error',
    suggested_category: 'Coordination Error',
    severity: 'Low',
    description: 'Temporary queue hold at central intersection while Atlas cleared crossing.',
    evidence: 'Inter-agent distance 1.4m triggered automated proximity pause for 4.2 seconds.',
    status: 'REVIEWED',
    timestamp: '06:16:12',
    location: 'Central Arterial Highway'
  }
];

export const MOCK_SAFETY_RULES = [
  {
    id: 'RULE-1',
    name: 'Inter-Agent Safe Separation (1.5m)',
    detail: 'Autonomous agents must maintain a minimum buffer of 1.5 meters from each other.',
    enforcedBy: 'Central Spatial Arbiter',
    action: 'Slow down at 2.5m, smooth brake hold at 1.0m'
  },
  {
    id: 'RULE-2',
    name: 'Work Zone Speed Limit (1.2 m/s)',
    detail: 'Maximum velocity governed inside picking, packing, and inspection corridors.',
    enforcedBy: 'Geofence Velocity Governor',
    action: 'Throttle governed automatically'
  },
  {
    id: 'RULE-3',
    name: 'Autonomous Obstacle Braking (0.1s)',
    detail: 'Unregistered obstacles trigger immediate stopping within 0.1 seconds.',
    enforcedBy: 'Onboard Collision Sensors',
    action: 'Immediate smooth stop until path is confirmed clear'
  },
  {
    id: 'RULE-4',
    name: 'Independent Task Verification',
    detail: 'AgentGuard audits physical station sensor readings before confirming task completion.',
    enforcedBy: 'AgentGuard Verification Engine',
    action: 'Flag Task Completion Error if payload weight is missing'
  }
];

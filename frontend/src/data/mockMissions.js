/**
 * Mock Missions and Trajectory Recording data conforming to design.md
 * RoboTrace stores chronological structured steps for each agent mission.
 */

export const MOCK_MISSIONS = [
  {
    id: 'MISSION-001',
    name: 'Morning Warehouse Fulfillment & Quality Audit',
    title: 'Autonomous Multi-Agent Pick & Transfer',
    status: 'In Progress',
    startTime: '2026-11-04 08:30:00',
    description: 'Executing coordinated package transport with Atlas, Nova, and Titan across Aisles A-D.',
    tasks: [
      { id: 'TASK-101', agentId: 'ATLAS', title: 'Pick package P-101 from Shelf A and deliver to Station B', status: 'Failed' },
      { id: 'TASK-102', agentId: 'NOVA', title: 'Inspect Shelves C and D for misplaced packages', status: 'Completed' },
      { id: 'TASK-103', agentId: 'TITAN', title: 'Transport material P-205 from Station X to Station Y', status: 'Completed' }
    ]
  },
  {
    id: 'MISSION-002',
    name: 'High-Bay Inventory Verification & Replenishment',
    title: 'High-Bay Verification & Pallet Relocate',
    status: 'Completed',
    startTime: '2026-11-04 06:15:00',
    description: 'Full facility scan and empty pallet retrieval from Loading Docks.',
    tasks: [
      { id: 'TASK-091', agentId: 'ATLAS', title: 'Retrieve Pallet Box P-088 from High-Bay B1', status: 'Completed' },
      { id: 'TASK-092', agentId: 'NOVA', title: 'Verify Stock Quantity on Shelves A1-A4', status: 'Completed' },
      { id: 'TASK-093', agentId: 'TITAN', title: 'Transfer empty pallets to Loading Dock Bay 2', status: 'Completed' }
    ]
  }
];

export const MOCK_TRAJECTORIES = {
  ATLAS: [
    {
      mission_id: 'MISSION-001',
      agent_id: 'ATLAS',
      step_id: 1,
      timestamp: '08:30:12',
      action_primitive: 'NAVIGATE',
      observation: 'Station B clear. Task received: Pick P-101 at Shelf A-2.',
      decision_summary: 'Compute shortest path to Shelf A-2 aisle.',
      action: 'NAVIGATE_TO_AISLE_A',
      expected_outcome: 'Reach Aisle A entry point without obstruction',
      actual_outcome: 'Reached Aisle A entry point at (x: -8.5, z: 2.0)',
      status: 'SUCCESS',
      position: { x: -8.5, y: 0.35, z: 2.0 },
      coordinates: { x: -8.5, y: 0.35, z: 2.0 },
      planned_coordinates: { x: -8.5, y: 0.35, z: 2.0 },
      heading: 90
    },
    {
      mission_id: 'MISSION-001',
      agent_id: 'ATLAS',
      step_id: 2,
      timestamp: '08:30:28',
      action_primitive: 'ALIGN',
      observation: 'Approaching Shelf A-2 picking location. Ground path clear.',
      decision_summary: 'Align arm gripper perpendicular to lower shelf beam.',
      action: 'ALIGN_GRIPPER_TO_SHELF',
      expected_outcome: 'Position gripper within 0.2m of Package P-101',
      actual_outcome: 'Alignment complete at Shelf A-2',
      status: 'SUCCESS',
      position: { x: -8.5, y: 0.35, z: -1.0 },
      coordinates: { x: -8.5, y: 0.35, z: -1.0 },
      planned_coordinates: { x: -8.5, y: 0.35, z: -1.0 },
      heading: 90
    },
    {
      mission_id: 'MISSION-001',
      agent_id: 'ATLAS',
      step_id: 3,
      timestamp: '08:30:45',
      action_primitive: 'AVOID',
      observation: 'Unregistered staging cart protruding 0.6m into travel envelope.',
      decision_summary: 'Attempt evasive lateral turn right without checking clearance margin.',
      action: 'MOVE_RIGHT_AVOIDANCE',
      expected_outcome: 'Bypass obstacle with 0.8m margin',
      actual_outcome: 'Left chassis bumper collided with Shelf A upright beam. Odometry halted.',
      status: 'FAILED',
      position: { x: -8.2, y: 0.35, z: -3.2 },
      coordinates: { x: -8.2, y: 0.35, z: -3.2 },
      planned_coordinates: { x: -8.5, y: 0.35, z: -4.5 },
      heading: 45,
      isErrorStep: true,
      errorId: 'ERR-201',
      error_detected: 'Collision Error (ERR-201)'
    },
    {
      mission_id: 'MISSION-001',
      agent_id: 'ATLAS',
      step_id: 4,
      timestamp: '08:31:02',
      action_primitive: 'GRASP',
      observation: 'Chassis impact detected. Package P-101 not engaged in gripper.',
      decision_summary: 'Grip closure attempted without optical verification of payload presence.',
      action: 'ACTUATE_GRIPPER_CLOSE',
      expected_outcome: 'Grasp package P-101 with 15N force',
      actual_outcome: 'Empty grip closure. Package remained on shelf.',
      status: 'FAILED',
      position: { x: -8.2, y: 0.35, z: -3.2 },
      coordinates: { x: -8.2, y: 0.35, z: -3.2 },
      planned_coordinates: { x: -8.5, y: 0.35, z: -4.5 },
      heading: 45,
      isErrorStep: true,
      errorId: 'ERR-202',
      error_detected: 'Manipulation Error (ERR-202)'
    },
    {
      mission_id: 'MISSION-001',
      agent_id: 'ATLAS',
      step_id: 5,
      timestamp: '08:31:25',
      action_primitive: 'REPORT',
      observation: 'Local policy timer elapsed. Package assumed picked.',
      decision_summary: 'Signal mission complete despite empty payload state.',
      action: 'REPORT_TASK_COMPLETED',
      expected_outcome: 'Deliver package P-101 to Station B',
      actual_outcome: 'Arrived at Station B empty. False task completion reported.',
      status: 'FAILED',
      position: { x: -4.0, y: 0.35, z: 15.0 },
      coordinates: { x: -4.0, y: 0.35, z: 15.0 },
      planned_coordinates: { x: -4.0, y: 0.35, z: 15.0 },
      heading: 0,
      isErrorStep: true,
      errorId: 'ERR-203',
      error_detected: 'Task Completion Error (ERR-203)'
    }
  ],
  NOVA: [
    {
      mission_id: 'MISSION-001',
      agent_id: 'NOVA',
      step_id: 1,
      timestamp: '08:30:15',
      action_primitive: 'ELEVATE',
      observation: 'Inspection mission active: High-Bay Racks C & D.',
      decision_summary: 'Elevate telescopic camera mast to shelf level 2 (1.8m).',
      action: 'EXTEND_MAST_ELEVATION',
      expected_outcome: 'Camera height 1.8m stabilized',
      actual_outcome: 'Mast extended, 4K RGB-D stream online',
      status: 'SUCCESS',
      position: { x: 8.5, y: 0.35, z: 2.0 },
      coordinates: { x: 8.5, y: 0.35, z: 2.0 },
      planned_coordinates: { x: 8.5, y: 0.35, z: 2.0 },
      heading: 270
    },
    {
      mission_id: 'MISSION-001',
      agent_id: 'NOVA',
      step_id: 2,
      timestamp: '08:30:40',
      action_primitive: 'SCAN',
      observation: 'Scanning barcode tags on Shelf C-1. All 14 boxes identified.',
      decision_summary: 'Cross-reference RFID tags against inventory database.',
      action: 'SCAN_INVENTORY_TAGS',
      expected_outcome: 'Verify 14 SKU matches',
      actual_outcome: 'All 14 SKUs matched expected database entries',
      status: 'SUCCESS',
      position: { x: 8.5, y: 0.35, z: 0.0 },
      coordinates: { x: 8.5, y: 0.35, z: 0.0 },
      planned_coordinates: { x: 8.5, y: 0.35, z: 0.0 },
      heading: 270
    },
    {
      mission_id: 'MISSION-001',
      agent_id: 'NOVA',
      step_id: 3,
      timestamp: '08:31:10',
      action_primitive: 'INSPECT',
      observation: 'Shelf D-2 inspection pass. Box SKU-904 misplaced in wrong bin.',
      decision_summary: 'Flag misplaced item and log coordinate for replenishment team.',
      action: 'LOG_INVENTORY_DISCREPANCY',
      expected_outcome: 'Generate discrepancy flag and proceed to Inspection Bay',
      actual_outcome: 'Discrepancy logged. Traveled to Quality Inspection Gantry.',
      status: 'SUCCESS',
      position: { x: 0.0, y: 0.35, z: 9.0 },
      coordinates: { x: 0.0, y: 0.35, z: 9.0 },
      planned_coordinates: { x: 0.0, y: 0.35, z: 9.0 },
      heading: 180
    }
  ],
  TITAN: [
    {
      mission_id: 'MISSION-001',
      agent_id: 'TITAN',
      step_id: 1,
      timestamp: '08:30:10',
      action_primitive: 'LIFT',
      observation: 'Material P-205 ready on pallet at Station X.',
      decision_summary: 'Drive below pallet, engage hydraulic scissor lift platform.',
      action: 'ENGAGE_SCISSOR_LIFT',
      expected_outcome: 'Lift 420kg cargo pallet 0.35m off floor',
      actual_outcome: 'Pallet secured on deck. Weight sensor confirms 420kg load.',
      status: 'SUCCESS',
      position: { x: 0.0, y: 0.35, z: -4.0 },
      coordinates: { x: 0.0, y: 0.35, z: -4.0 },
      planned_coordinates: { x: 0.0, y: 0.35, z: -4.0 },
      heading: 180
    },
    {
      mission_id: 'MISSION-001',
      agent_id: 'TITAN',
      step_id: 2,
      timestamp: '08:30:35',
      action_primitive: 'TRANSIT',
      observation: 'Transit corridor active. Atlas operating in west quadrant.',
      decision_summary: 'Navigate central 4.5m arterial highway at governed 1.6 m/s.',
      action: 'TRANSIT_CENTRAL_HIGHWAY',
      expected_outcome: 'Maintain safe 2.5m separation from intersections',
      actual_outcome: 'Reached south intersection smoothly',
      status: 'SUCCESS',
      position: { x: 0.0, y: 0.35, z: -10.0 },
      coordinates: { x: 0.0, y: 0.35, z: -10.0 },
      planned_coordinates: { x: 0.0, y: 0.35, z: -10.0 },
      heading: 180
    },
    {
      mission_id: 'MISSION-001',
      agent_id: 'TITAN',
      step_id: 3,
      timestamp: '08:31:05',
      action_primitive: 'LOWER',
      observation: 'Arrived at Loading Dock Bay 1. Dock plate leveler clear.',
      decision_summary: 'Lower scissor platform and release wooden pallet.',
      action: 'LOWER_PLATFORM_DELIVERY',
      expected_outcome: 'Disengage pallet cleanly onto staging floor',
      actual_outcome: 'Pallet successfully staged at Loading Dock Bay 1',
      status: 'SUCCESS',
      position: { x: 4.0, y: 0.35, z: -14.0 },
      coordinates: { x: 4.0, y: 0.35, z: -14.0 },
      planned_coordinates: { x: 4.0, y: 0.35, z: -14.0 },
      heading: 180
    }
  ]
};

export const WAREHOUSE_DESTINATIONS = [
  { id: 'dest-rack-a1', name: 'Shelf Rack A-1 (Storage West)', category: 'Storage', position: { x: -8.5, y: 0, z: 4.5 } },
  { id: 'dest-rack-a2', name: 'Shelf Rack A-2 (Picking Aisle)', category: 'Storage', position: { x: -8.5, y: 0, z: -4.5 } },
  { id: 'dest-rack-b1', name: 'High-Bay Rack B-1 (Inventory East)', category: 'Storage', position: { x: 8.5, y: 0, z: 4.5 } },
  { id: 'dest-rack-b2', name: 'High-Bay Rack B-2 (Scanning Aisle)', category: 'Storage', position: { x: 8.5, y: 0, z: -4.5 } },
  { id: 'dest-inspect', name: 'Quality Inspection Bay (Scanner Gantry)', category: 'Inspection', position: { x: 0.0, y: 0, z: 9.0 } },
  { id: 'dest-pack-1', name: 'Packing & Order Prep Station', category: 'Processing', position: { x: -4.0, y: 0, z: 15.0 } },
  { id: 'dest-ship-1', name: 'Loading Dock Bay 1 (Inbound)', category: 'Shipping', position: { x: 4.0, y: 0, z: -14.0 } },
  { id: 'dest-ship-2', name: 'Loading Dock Bay 2 (Outbound)', category: 'Shipping', position: { x: 8.5, y: 0, z: -14.0 } },
  { id: 'dest-charge-1', name: 'Charging Bay 1 (Docking Station)', category: 'Charging', position: { x: -11.0, y: 0, z: -14.0 } },
  { id: 'dest-charge-2', name: 'Charging Bay 2 (Docking Station)', category: 'Charging', position: { x: -7.5, y: 0, z: -14.0 } }
];

export const MOCK_ROBOTS = [
  {
    id: 'atlas',
    name: 'Atlas',
    type: 'Arm Picker',
    tagline: 'Robotic Arm & Package Gripper',
    status: 'In Transit',
    currentAction: 'Reaching & Picking Package',
    battery: 88,
    speed: 1.4,
    position: { x: -8.5, y: 0.35, z: 2.0 },
    startPosition: { x: -8.5, y: 0.35, z: 2.0 },
    heading: 90,
    destination: 'Shelf Rack A-2 (Picking Aisle)',
    targetCoords: { x: -8.5, y: 0, z: -4.5 },
    payload: {
      item: 'Fragile Electronics Box',
      weight: '8.4 kg',
      status: 'Gripped securely'
    },
    equipment: '6-Axis Articulated Arm + Dual-Finger Gripper',
    sensors: '3D Depth Camera, Lidar, Grip Force Sensor',
    health: '100% Operational',
    color: '#ea580c', // Industrial Orange
    waypoints: [
      { x: -8.5, y: 0, z: 2.0 },
      { x: -8.5, y: 0, z: -1.0 },
      { x: -8.5, y: 0, z: -4.5 }
    ]
  },
  {
    id: 'nova',
    name: 'Nova',
    type: 'Shelf Scanner',
    tagline: 'Inspection Mast & Camera Scanner',
    status: 'Scanning',
    currentAction: 'Scanning Shelf Inventory',
    battery: 76,
    speed: 1.1,
    position: { x: 8.5, y: 0.35, z: 2.0 },
    startPosition: { x: 8.5, y: 0.35, z: 2.0 },
    heading: 270,
    destination: 'Quality Inspection Bay (Scanner Gantry)',
    targetCoords: { x: 0.0, y: 0, z: 9.0 },
    payload: {
      item: 'Barcode & RFID Scanner',
      weight: '4.2 kg',
      status: 'Active scanning mode'
    },
    equipment: 'Telescopic Sensor Mast + Pan-Tilt Dual 4K Camera',
    sensors: 'Barcode Reader, Thermal Sensor, Range Finder',
    health: '100% Operational',
    color: '#2563eb', // Cobalt Blue
    waypoints: [
      { x: 8.5, y: 0, z: 2.0 },
      { x: 8.5, y: 0, z: 0.0 },
      { x: 0.0, y: 0, z: 0.0 },
      { x: 0.0, y: 0, z: 9.0 }
    ]
  },
  {
    id: 'titan',
    name: 'Titan',
    type: 'Pallet Transporter',
    tagline: 'Hydraulic Scissor Lift Platform',
    status: 'Moving',
    currentAction: 'Elevating & Moving Pallet',
    battery: 64,
    speed: 1.6,
    position: { x: 0.0, y: 0.35, z: -4.0 },
    startPosition: { x: 0.0, y: 0.35, z: -4.0 },
    heading: 180,
    destination: 'Loading Dock Bay 1 (Inbound)',
    targetCoords: { x: 4.0, y: 0, z: -14.0 },
    payload: {
      item: 'Pallet of 12 Heavy Cartons',
      weight: '420 kg',
      status: 'Lifted onto platform'
    },
    equipment: 'Motorized Scissor Lift + Heavy Duty Wheelbase',
    sensors: 'Ground Sensors, Obstacle Radar, Weight Scales',
    health: '100% Operational',
    color: '#ca8a04', // Industrial Yellow-Gold
    waypoints: [
      { x: 0.0, y: 0, z: -4.0 },
      { x: 0.0, y: 0, z: -10.0 },
      { x: 4.0, y: 0, z: -10.0 },
      { x: 4.0, y: 0, z: -14.0 }
    ]
  }
];

export const MOCK_FLEET_SUMMARY = {
  totalRobots: 3,
  activeRobots: 3,
  inTransit: 2,
  idleRobots: 0,
  chargingRobots: 0,
  averageBattery: 76,
  packagesHandledToday: 348,
  distanceTraveledKm: 42.6,
  systemSafetyStatus: 'Safe & Clear'
};

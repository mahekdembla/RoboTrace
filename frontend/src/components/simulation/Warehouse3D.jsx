import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import * as THREE from 'three';
import { Robot } from './Robot';
import { TrajectoryPath } from './TrajectoryPath';

/**
 * Realistic Industrial Storage Rack (Steel blue uprights & orange load beams)
 */
function StorageRack({ position = [0, 0, 0], length = 7.5, height = 3.8 }) {
  return (
    <group position={position}>
      {/* Blue Vertical Upright Frame Posts */}
      {[-length / 2, 0, length / 2].map((x, i) => (
        <group key={`frame-${i}`} position={[x, height / 2, 0]}>
          <mesh castShadow position={[0, 0, -0.68]}>
            <boxGeometry args={[0.1, height, 0.1]} />
            <meshStandardMaterial color="#1d4ed8" metalness={0.7} roughness={0.3} />
          </mesh>
          <mesh castShadow position={[0, 0, 0.68]}>
            <boxGeometry args={[0.1, height, 0.1]} />
            <meshStandardMaterial color="#1d4ed8" metalness={0.7} roughness={0.3} />
          </mesh>
          {/* Diagonal steel bracing */}
          <mesh position={[0, 0, 0]} rotation={[0.38, 0, 0]}>
            <boxGeometry args={[0.04, height * 0.9, 0.04]} />
            <meshStandardMaterial color="#64748b" metalness={0.8} />
          </mesh>
        </group>
      ))}

      {/* Safety Yellow End-Cap Collision Bollards */}
      {[-length / 2 - 0.35, length / 2 + 0.35].map((bx, bi) =>
        [-0.8, 0.8].map((bz, bzi) => (
          <group key={`bollard-${bi}-${bzi}`} position={[bx, 0.45, bz]}>
            <mesh castShadow>
              <cylinderGeometry args={[0.1, 0.1, 0.9, 16]} />
              <meshStandardMaterial color="#eab308" roughness={0.3} metalness={0.2} />
            </mesh>
            {/* Black warning stripe */}
            <mesh position={[0, 0.15, 0]}>
              <cylinderGeometry args={[0.102, 0.102, 0.2, 16]} />
              <meshStandardMaterial color="#0f172a" />
            </mesh>
          </group>
        ))
      )}

      {/* Horizontal Safety Orange Beams & Pallet Loads */}
      {[0.8, 1.8, 2.8].map((y, level) => (
        <group key={`shelf-${level}`} position={[0, y, 0]}>
          {/* Front & Back Orange Load Beams */}
          <mesh position={[0, 0, 0.68]}>
            <boxGeometry args={[length + 0.1, 0.1, 0.05]} />
            <meshStandardMaterial color="#ea580c" roughness={0.4} />
          </mesh>
          <mesh position={[0, 0, -0.68]}>
            <boxGeometry args={[length + 0.1, 0.1, 0.05]} />
            <meshStandardMaterial color="#ea580c" roughness={0.4} />
          </mesh>

          {/* Wooden Pallets & Cardboard Packages */}
          {[-length / 3, 0, length / 3].map((cx, ci) => (
            <group key={`box-group-${ci}`} position={[cx, 0.15, 0]}>
              {/* Wooden Pallet */}
              <mesh position={[0, 0.04, 0]} castShadow>
                <boxGeometry args={[1.35, 0.08, 1.15]} />
                <meshStandardMaterial color="#d97706" roughness={0.9} />
              </mesh>
              {/* Cardboard Boxes */}
              <mesh position={[0, 0.32, 0]} castShadow>
                <boxGeometry args={[1.15, 0.48, 1.0]} />
                <meshStandardMaterial
                  color={ci % 2 === 0 ? '#b45309' : '#92400e'}
                  roughness={0.8}
                />
              </mesh>
              {/* White Shipping Label */}
              <mesh position={[0.58, 0.35, 0]}>
                <planeGeometry args={[0.2, 0.14]} />
                <meshBasicMaterial color="#ffffff" side={THREE.DoubleSide} />
              </mesh>
            </group>
          ))}
        </group>
      ))}
    </group>
  );
}

/**
 * Quality Inspection Station with Overhead Scanner Gantry
 */
function InspectionStation({ position = [0, 0, 0] }) {
  return (
    <group position={position}>
      {/* Floor Inspection Boundary Area */}
      <mesh position={[0, 0.012, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[5.2, 4.2]} />
        <meshStandardMaterial color="#1e293b" />
      </mesh>
      {/* Green Inspection Guide Ring */}
      <mesh position={[0, 0.018, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[2.0, 2.1, 32]} />
        <meshBasicMaterial color="#10b981" />
      </mesh>

      {/* Overhead Scanner Gantry Frame */}
      <group position={[0, 2.2, 0]}>
        {/* Left & Right Vertical Columns */}
        <mesh position={[-2.4, -0.7, 0]} castShadow>
          <boxGeometry args={[0.16, 3.2, 0.16]} />
          <meshStandardMaterial color="#334155" metalness={0.8} />
        </mesh>
        <mesh position={[2.4, -0.7, 0]} castShadow>
          <boxGeometry args={[0.16, 3.2, 0.16]} />
          <meshStandardMaterial color="#334155" metalness={0.8} />
        </mesh>
        {/* Top Horizontal Scanner Bridge */}
        <mesh position={[0, 0.8, 0]} castShadow>
          <boxGeometry args={[5.0, 0.2, 0.3]} />
          <meshStandardMaterial color="#0f172a" metalness={0.7} />
        </mesh>
        {/* Overhead Camera Sensors & Downward Verification Beam */}
        {[-1.2, 0, 1.2].map((sx, si) => (
          <group key={`sens-${si}`} position={[sx, 0.6, 0]}>
            <mesh>
              <cylinderGeometry args={[0.1, 0.12, 0.2, 16]} />
              <meshStandardMaterial color="#2563eb" metalness={0.9} />
            </mesh>
            <mesh position={[0, -0.6, 0]}>
              <coneGeometry args={[0.45, 1.2, 16, 1, true]} />
              <meshBasicMaterial
                color="#10b981"
                transparent
                opacity={0.12}
                side={THREE.DoubleSide}
              />
            </mesh>
          </group>
        ))}
      </group>
    </group>
  );
}

/**
 * Order Packing & Prep Workstation Zone
 */
function PackingZone({ position = [0, 0, 0] }) {
  return (
    <group position={position}>
      {/* Floor Zone */}
      <mesh position={[0, 0.012, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[11, 4.5]} />
        <meshStandardMaterial color="#334155" />
      </mesh>
      {/* Blue Boundary Lines */}
      <mesh position={[0, 0.018, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[2.5, 2.58, 4]} />
        <meshBasicMaterial color="#3b82f6" />
      </mesh>

      {/* Conveyor Roller Table */}
      <group position={[0, 0.45, 0]}>
        <mesh position={[0, 0, 0]} castShadow>
          <boxGeometry args={[8.0, 0.15, 1.1]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        {/* Conveyor Rollers */}
        {[-3.2, -2.4, -1.6, -0.8, 0, 0.8, 1.6, 2.4, 3.2].map((rx, ri) => (
          <mesh key={`roller-${ri}`} position={[rx, 0.1, 0]} rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.06, 0.06, 1.05, 16]} />
            <meshStandardMaterial color="#94a3b8" metalness={0.9} roughness={0.2} />
          </mesh>
        ))}
        {/* Conveyor Legs */}
        {[-3.5, 0, 3.5].map((lx, li) => (
          <mesh key={`cleg-${li}`} position={[lx, -0.22, 0]}>
            <boxGeometry args={[0.1, 0.45, 0.9]} />
            <meshStandardMaterial color="#1e293b" />
          </mesh>
        ))}
        {/* Packages on Conveyor */}
        {[-2.0, 0.5, 2.2].map((px, pi) => (
          <mesh key={`pack-${pi}`} position={[px, 0.28, 0]} castShadow>
            <boxGeometry args={[0.55, 0.35, 0.5]} />
            <meshStandardMaterial color="#b45309" roughness={0.8} />
          </mesh>
        ))}
      </group>
    </group>
  );
}

/**
 * Truck Loading & Unloading Dock Bays
 */
function LoadingDockBays({ position = [0, 0, 0] }) {
  return (
    <group position={position}>
      {/* 2 Loading Bays */}
      {[0, 5.0].map((bx, bi) => (
        <group key={`dock-${bi}`} position={[bx, 0, 0]}>
          {/* Staging Floor Pad */}
          <mesh position={[0, 0.014, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[3.8, 4.5]} />
            <meshStandardMaterial color="#1e293b" />
          </mesh>
          {/* Yellow Safety Hazard Boundary */}
          <mesh position={[0, 0.018, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[1.8, 1.9, 4]} />
            <meshBasicMaterial color="#eab308" />
          </mesh>
          {/* Rollup Door Backstop Frame */}
          <group position={[0, 1.8, -2.25]}>
            <mesh castShadow>
              <boxGeometry args={[3.4, 3.5, 0.2]} />
              <meshStandardMaterial color="#475569" metalness={0.6} />
            </mesh>
            {/* Yellow Dock Plate Leveler on floor */}
            <mesh position={[0, -1.78, 0.6]} rotation={[-Math.PI / 2, 0, 0]}>
              <planeGeometry args={[2.4, 1.2]} />
              <meshStandardMaterial color="#eab308" metalness={0.8} />
            </mesh>
          </group>
          {/* Stacked Cargo Pallets in Staging Area */}
          <mesh position={[-0.8, 0.2, 0.5]} castShadow>
            <boxGeometry args={[1.2, 0.4, 1.1]} />
            <meshStandardMaterial color="#b45309" roughness={0.8} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

/**
 * Dedicated Autonomous Charging Stations
 */
function ChargingBays({ position = [0, 0, 0] }) {
  return (
    <group position={position}>
      {[0, 3.5].map((cx, ci) => (
        <group key={`charge-${ci}`} position={[cx, 0, 0]}>
          {/* Charging Pad */}
          <mesh position={[0, 0.015, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[2.0, 2.4]} />
            <meshStandardMaterial color="#0f172a" />
          </mesh>
          {/* Emerald Glow Ring */}
          <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[0.85, 0.95, 4]} />
            <meshBasicMaterial color="#10b981" />
          </mesh>
          {/* Vertical Terminal Pillar */}
          <mesh position={[-0.9, 0.8, 0]} castShadow>
            <boxGeometry args={[0.26, 1.6, 0.45]} />
            <meshStandardMaterial color="#334155" metalness={0.7} />
          </mesh>
          {/* Green Status Light */}
          <mesh position={[-0.75, 1.4, 0]}>
            <sphereGeometry args={[0.07, 16, 16]} />
            <meshBasicMaterial color="#10b981" />
          </mesh>
        </group>
      ))}
    </group>
  );
}

/**
 * Main 3D Warehouse Environment
 */
export function Warehouse3D({
  robots = [],
  selectedRobotId,
  onSelectRobot,
  showTrajectories = true
}) {
  return (
    <div className="w-full h-full relative overflow-hidden bg-slate-300">
      <Canvas
        shadows
        camera={{ position: [18, 20, 24], fov: 44 }}
        gl={{ antialias: true }}
      >
        <Suspense fallback={null}>
          <OrbitControls
            enableDamping
            dampingFactor={0.05}
            maxPolarAngle={Math.PI / 2 - 0.04}
            minDistance={5}
            maxDistance={65}
            target={[0, 0.5, 0]}
          />

          {/* Clean, Realistic Industrial Lighting */}
          <ambientLight intensity={0.95} color="#ffffff" />
          <directionalLight
            position={[22, 28, 18]}
            intensity={1.4}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
            shadow-bias={-0.0001}
            color="#fffbeb"
          />
          {/* Secondary Fill Light */}
          <directionalLight position={[-18, 20, -16]} intensity={0.65} color="#e2e8f0" />

          {/* Darker Light-Grey Polished Concrete Floor */}
          <mesh
            rotation={[-Math.PI / 2, 0, 0]}
            position={[0, -0.01, 0]}
            receiveShadow
          >
            <planeGeometry args={[68, 52]} />
            <meshStandardMaterial
              color="#94a3b8" /* Darker light-grey slate-400 for high contrast */
              roughness={0.35}
              metalness={0.15}
            />
          </mesh>

          {/* Subtle Engineering Floor Subdivision Grid */}
          <Grid
            position={[0, 0, 0]}
            args={[64, 48]}
            cellSize={1}
            cellThickness={0.4}
            cellColor="#cbd5e1"
            sectionSize={4}
            sectionThickness={0.9}
            sectionColor="#64748b"
            fadeDistance={45}
            fadeStrength={1.2}
          />

          {/* Central Arterial Highway (Wide 4.5m Main Aisle along Z) */}
          <mesh position={[0, 0.005, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[4.5, 38]} />
            <meshStandardMaterial color="#cbd5e1" roughness={0.4} />
          </mesh>
          {/* Yellow Boundary Lines */}
          <mesh position={[-2.25, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[0.1, 38]} />
            <meshBasicMaterial color="#eab308" />
          </mesh>
          <mesh position={[2.25, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[0.1, 38]} />
            <meshBasicMaterial color="#eab308" />
          </mesh>

          {/* East-West Cross-Corridor (Wide 4.0m Aisle along X) */}
          <mesh position={[0, 0.006, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[36, 4.0]} />
            <meshStandardMaterial color="#cbd5e1" roughness={0.4} />
          </mesh>
          <mesh position={[0, 0.011, -2.0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[36, 0.1]} />
            <meshBasicMaterial color="#eab308" />
          </mesh>
          <mesh position={[0, 0.011, 2.0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[36, 0.1]} />
            <meshBasicMaterial color="#eab308" />
          </mesh>

          {/* Pedestrian Zebra Crossings at Center Intersection */}
          {[-1.2, -0.6, 0, 0.6, 1.2].map((zx, zi) => (
            <mesh key={`cross-${zi}`} position={[zx, 0.012, 0]} rotation={[-Math.PI / 2, 0, 0]}>
              <planeGeometry args={[0.3, 3.8]} />
              <meshStandardMaterial color="#f8fafc" />
            </mesh>
          ))}

          {/* MULTIPLE SHELF ROWS (Expanded Storage Racks) */}
          {/* West Storage Block: Row 1 & Row 2 */}
          <StorageRack position={[-11.5, 0, 5.5]} length={8.5} />
          <StorageRack position={[-11.5, 0, -5.5]} length={8.5} />
          <StorageRack position={[-6.0, 0, 5.5]} length={8.5} />
          <StorageRack position={[-6.0, 0, -5.5]} length={8.5} />

          {/* East High-Bay Storage Block: Row 3 & Row 4 */}
          <StorageRack position={[6.0, 0, 5.5]} length={8.5} />
          <StorageRack position={[6.0, 0, -5.5]} length={8.5} />
          <StorageRack position={[11.5, 0, 5.5]} length={8.5} />
          <StorageRack position={[11.5, 0, -5.5]} length={8.5} />

          {/* FUNCTIONAL WAREHOUSE ZONES */}
          {/* 1. Quality Inspection Bay (Scanner Gantry) */}
          <InspectionStation position={[0, 0, 9.0]} />

          {/* 2. Order Packing & Prep Workstation Zone */}
          <PackingZone position={[0, 0, 15.5]} />

          {/* 3. Loading & Unloading Dock Bays */}
          <LoadingDockBays position={[4.0, 0, -14.0]} />

          {/* 4. Autonomous Charging Docks */}
          <ChargingBays position={[-11.0, 0, -14.0]} />

          {/* Planned Trajectory Paths */}
          {showTrajectories &&
            robots.map((robot) => (
              <TrajectoryPath
                key={`route-${robot.id}`}
                historyPoints={robot.waypoints}
                plannedPoints={robot.waypoints}
                color={robot.color}
                showWaypoints={robot.id === selectedRobotId}
                showPlanned={true}
              />
            ))}

          {/* Visible Interactive Robots (Atlas, Nova, Titan) */}
          {robots.map((robot) => (
            <Robot
              key={robot.id}
              robot={robot}
              isSelected={robot.id === selectedRobotId}
              onSelect={onSelectRobot}
            />
          ))}
        </Suspense>
      </Canvas>
    </div>
  );
}

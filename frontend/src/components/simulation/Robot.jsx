import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

/**
 * 1. ATLAS: Robotic Arm & Gripper for picking packages
 */
function AtlasModel() {
  const armBaseRef = useRef();
  const elbowRef = useRef();
  const gripperLeftRef = useRef();
  const gripperRightRef = useRef();
  const packageRef = useRef();

  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    if (armBaseRef.current) {
      // Rotate shoulder towards shelf and back
      armBaseRef.current.rotation.y = Math.sin(t * 1.5) * 0.45;
    }
    if (elbowRef.current) {
      // Articulate elbow reaching down and lifting
      elbowRef.current.rotation.z = -0.4 + Math.sin(t * 1.5) * 0.25;
    }
    if (gripperLeftRef.current && gripperRightRef.current) {
      // Gripper fingers open and close
      const gripSpan = 0.08 + Math.sin(t * 3) * 0.04;
      gripperLeftRef.current.position.z = gripSpan;
      gripperRightRef.current.position.z = -gripSpan;
    }
    if (packageRef.current) {
      // Package moves with gripper
      packageRef.current.position.y = 0.85 + Math.sin(t * 1.5) * 0.12;
    }
  });

  return (
    <group position={[0, 0.35, 0]}>
      {/* Base Chassis - Industrial Safety Orange */}
      <mesh castShadow receiveShadow position={[0, 0.15, 0]}>
        <boxGeometry args={[1.6, 0.45, 1.2]} />
        <meshStandardMaterial color="#ea580c" roughness={0.3} metalness={0.4} />
      </mesh>

      {/* Heavy Wheel Assemblies */}
      {[-0.6, 0.6].map((x) =>
        [-0.68, 0.68].map((z) => (
          <mesh key={`${x}-${z}`} position={[x, 0, z]} rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.22, 0.22, 0.16, 24]} />
            <meshStandardMaterial color="#1e293b" roughness={0.8} />
          </mesh>
        ))
      )}

      {/* Shoulder Turntable */}
      <group ref={armBaseRef} position={[0.2, 0.4, 0]}>
        <mesh castShadow position={[0, 0.1, 0]}>
          <cylinderGeometry args={[0.3, 0.35, 0.2, 24]} />
          <meshStandardMaterial color="#334155" metalness={0.7} roughness={0.3} />
        </mesh>

        {/* Lower Arm (Bicep) */}
        <mesh castShadow position={[0, 0.45, 0]}>
          <boxGeometry args={[0.16, 0.65, 0.16]} />
          <meshStandardMaterial color="#f97316" metalness={0.5} roughness={0.4} />
        </mesh>

        {/* Elbow Joint */}
        <group ref={elbowRef} position={[0, 0.8, 0]}>
          <mesh castShadow>
            <sphereGeometry args={[0.14, 16, 16]} />
            <meshStandardMaterial color="#0f172a" metalness={0.8} />
          </mesh>

          {/* Forearm */}
          <mesh castShadow position={[0.3, 0.1, 0]} rotation={[0, 0, -Math.PI / 4]}>
            <boxGeometry args={[0.14, 0.55, 0.14]} />
            <meshStandardMaterial color="#334155" metalness={0.6} />
          </mesh>

          {/* Wrist Joint */}
          <group position={[0.55, 0.35, 0]}>
            <mesh castShadow>
              <cylinderGeometry args={[0.09, 0.09, 0.12, 16]} />
              <meshStandardMaterial color="#0f172a" />
            </mesh>

            {/* Gripper Base Plate */}
            <mesh position={[0.1, 0, 0]}>
              <boxGeometry args={[0.08, 0.18, 0.26]} />
              <meshStandardMaterial color="#475569" metalness={0.8} />
            </mesh>

            {/* Parallel Gripper Fingers */}
            <mesh ref={gripperLeftRef} position={[0.2, 0, 0.1]}>
              <boxGeometry args={[0.18, 0.06, 0.04]} />
              <meshStandardMaterial color="#1e293b" metalness={0.9} />
            </mesh>
            <mesh ref={gripperRightRef} position={[0.2, 0, -0.1]}>
              <boxGeometry args={[0.18, 0.06, 0.04]} />
              <meshStandardMaterial color="#1e293b" metalness={0.9} />
            </mesh>

            {/* Picked Cardboard Box Package */}
            <group ref={packageRef} position={[0.25, 0, 0]}>
              <mesh castShadow>
                <boxGeometry args={[0.28, 0.28, 0.28]} />
                <meshStandardMaterial color="#b45309" roughness={0.8} />
              </mesh>
              {/* Shipping Tape */}
              <mesh position={[0, 0.142, 0]}>
                <boxGeometry args={[0.06, 0.01, 0.282]} />
                <meshStandardMaterial color="#fde68a" />
              </mesh>
            </group>
          </group>
        </group>
      </group>
    </group>
  );
}

/**
 * 2. NOVA: Tall Camera & Sensor Mast for inspecting shelves
 */
function NovaModel() {
  const mastRef = useRef();
  const cameraHeadRef = useRef();

  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    if (mastRef.current) {
      // Mast gently extends up and down
      mastRef.current.position.y = 0.95 + Math.sin(t * 1.2) * 0.15;
    }
    if (cameraHeadRef.current) {
      // Pan camera head left and right across shelves
      cameraHeadRef.current.rotation.y = Math.sin(t * 2) * 0.7;
      cameraHeadRef.current.rotation.x = Math.sin(t * 1.5) * 0.15;
    }
  });

  return (
    <group position={[0, 0.35, 0]}>
      {/* Base Chassis - Arctic White with Cobalt Blue Accents */}
      <mesh castShadow receiveShadow position={[0, 0.14, 0]}>
        <boxGeometry args={[1.5, 0.4, 1.1]} />
        <meshStandardMaterial color="#ffffff" roughness={0.2} metalness={0.2} />
      </mesh>
      {/* Cobalt Side Trim */}
      <mesh position={[0, 0.14, 0.56]}>
        <boxGeometry args={[1.4, 0.1, 0.04]} />
        <meshStandardMaterial color="#2563eb" />
      </mesh>
      <mesh position={[0, 0.14, -0.56]}>
        <boxGeometry args={[1.4, 0.1, 0.04]} />
        <meshStandardMaterial color="#2563eb" />
      </mesh>

      {/* Wheels */}
      {[-0.55, 0.55].map((x) =>
        [-0.6, 0.6].map((z) => (
          <mesh key={`${x}-${z}`} position={[x, 0, z]} rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.2, 0.2, 0.14, 24]} />
            <meshStandardMaterial color="#1e293b" />
          </mesh>
        ))
      )}

      {/* Vertical Inspection Tower Mast */}
      <mesh castShadow position={[0, 0.6, 0]}>
        <cylinderGeometry args={[0.08, 0.1, 0.9, 16]} />
        <meshStandardMaterial color="#64748b" metalness={0.8} />
      </mesh>

      {/* Telescopic Upper Mast Section */}
      <group ref={mastRef} position={[0, 0.95, 0]}>
        <mesh castShadow>
          <cylinderGeometry args={[0.06, 0.06, 0.6, 16]} />
          <meshStandardMaterial color="#cbd5e1" metalness={0.9} />
        </mesh>

        {/* Pan-Tilt Camera Head */}
        <group ref={cameraHeadRef} position={[0, 0.35, 0]}>
          <mesh castShadow>
            <boxGeometry args={[0.28, 0.2, 0.35]} />
            <meshStandardMaterial color="#0f172a" roughness={0.3} metalness={0.7} />
          </mesh>

          {/* Dual 4K Camera Lenses */}
          <mesh position={[0.15, 0.04, 0.08]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.05, 0.06, 0.06, 16]} />
            <meshStandardMaterial color="#38bdf8" metalness={0.9} roughness={0.1} />
          </mesh>
          <mesh position={[0.15, 0.04, -0.08]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.05, 0.06, 0.06, 16]} />
            <meshStandardMaterial color="#38bdf8" metalness={0.9} roughness={0.1} />
          </mesh>

          {/* Visible Shelf Inspection Scanning Light Cone */}
          <mesh position={[0.8, 0, 0]} rotation={[0, 0, -Math.PI / 2]}>
            <coneGeometry args={[0.6, 1.4, 16, 1, true]} />
            <meshBasicMaterial
              color="#38bdf8"
              transparent
              opacity={0.18}
              side={THREE.DoubleSide}
            />
          </mesh>
        </group>
      </group>
    </group>
  );
}

/**
 * 3. TITAN: Heavy Pallet Transporter with Motorized Scissor Lift
 */
function TitanModel() {
  const liftPlatformRef = useRef();

  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    if (liftPlatformRef.current) {
      // Platform smoothly raises up to 0.4m and lowers
      liftPlatformRef.current.position.y = 0.35 + (Math.sin(t * 1.0) + 1) * 0.18;
    }
  });

  return (
    <group position={[0, 0.35, 0]}>
      {/* Heavy Base Transporter Chassis - Safety Yellow */}
      <mesh castShadow receiveShadow position={[0, 0.12, 0]}>
        <boxGeometry args={[1.8, 0.35, 1.3]} />
        <meshStandardMaterial color="#ca8a04" roughness={0.4} metalness={0.3} />
      </mesh>

      {/* Safety Hazard Stripes On Bumper */}
      <mesh position={[0.91, 0.12, 0]}>
        <boxGeometry args={[0.02, 0.25, 1.1]} />
        <meshStandardMaterial color="#1e293b" />
      </mesh>
      <mesh position={[-0.91, 0.12, 0]}>
        <boxGeometry args={[0.02, 0.25, 1.1]} />
        <meshStandardMaterial color="#1e293b" />
      </mesh>

      {/* Industrial Wheel Sets */}
      {[-0.65, 0, 0.65].map((x) =>
        [-0.72, 0.72].map((z) => (
          <mesh key={`${x}-${z}`} position={[x, 0, z]} rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.22, 0.22, 0.14, 24]} />
            <meshStandardMaterial color="#0f172a" />
          </mesh>
        ))
      )}

      {/* Motorized Scissor Lift Mechanism & Upper Pallet Deck */}
      <group ref={liftPlatformRef} position={[0, 0.35, 0]}>
        {/* Scissor Cross Bars */}
        <mesh position={[0, -0.15, 0.45]} rotation={[0, 0, 0.35]}>
          <boxGeometry args={[0.8, 0.05, 0.04]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        <mesh position={[0, -0.15, 0.45]} rotation={[0, 0, -0.35]}>
          <boxGeometry args={[0.8, 0.05, 0.04]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        <mesh position={[0, -0.15, -0.45]} rotation={[0, 0, 0.35]}>
          <boxGeometry args={[0.8, 0.05, 0.04]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        <mesh position={[0, -0.15, -0.45]} rotation={[0, 0, -0.35]}>
          <boxGeometry args={[0.8, 0.05, 0.04]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>

        {/* Steel Lifting Deck */}
        <mesh castShadow receiveShadow position={[0, 0, 0]}>
          <boxGeometry args={[1.7, 0.08, 1.25]} />
          <meshStandardMaterial color="#334155" metalness={0.7} roughness={0.3} />
        </mesh>

        {/* Wooden Cargo Pallet */}
        <group position={[0, 0.12, 0]}>
          <mesh castShadow>
            <boxGeometry args={[1.4, 0.12, 1.1]} />
            <meshStandardMaterial color="#d97706" roughness={0.85} />
          </mesh>

          {/* Stacked Cargo Delivery Packages */}
          {[-0.35, 0.35].map((bx) =>
            [-0.25, 0.25].map((bz) => (
              <mesh key={`crate-${bx}-${bz}`} position={[bx, 0.3, bz]} castShadow>
                <boxGeometry args={[0.55, 0.45, 0.45]} />
                <meshStandardMaterial color="#b45309" roughness={0.8} />
              </mesh>
            ))
          )}
        </group>
      </group>
    </group>
  );
}

/**
 * Universal Robot Wrapper with Visible Actions and Hover-Only Tooltip
 */
export function Robot({
  robot,
  isSelected = false,
  onSelect
}) {
  const [isHovered, setIsHovered] = useState(false);

  if (!robot) return null;

  const { position, heading = 0, status, id, name, speed } = robot;

  return (
    <group
      position={[position.x, position.y || 0, position.z]}
      rotation={[0, THREE.MathUtils.degToRad(heading), 0]}
      onPointerOver={(e) => {
        e.stopPropagation();
        setIsHovered(true);
        document.body.style.cursor = 'pointer';
      }}
      onPointerOut={() => {
        setIsHovered(false);
        document.body.style.cursor = 'auto';
      }}
      onClick={(e) => {
        e.stopPropagation();
        if (onSelect) onSelect(id);
      }}
    >
      {/* High-visibility Selection Indicator on Floor */}
      {isSelected && (
        <group position={[0, -0.28, 0]}>
          {/* Outer primary ring */}
          <mesh rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[1.4, 1.58, 32]} />
            <meshBasicMaterial color="#2563eb" side={THREE.DoubleSide} />
          </mesh>
          {/* Inner highlight ring */}
          <mesh rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[1.65, 1.72, 32]} />
            <meshBasicMaterial color="#3b82f6" transparent opacity={0.6} side={THREE.DoubleSide} />
          </mesh>
          {/* Soft blue ground fill */}
          <mesh rotation={[-Math.PI / 2, 0, 0]}>
            <circleGeometry args={[1.4, 32]} />
            <meshBasicMaterial
              color="#2563eb"
              transparent
              opacity={0.16}
              side={THREE.DoubleSide}
            />
          </mesh>
        </group>
      )}

      {/* Render Specific Robot Model */}
      {id === 'atlas' && <AtlasModel />}
      {id === 'nova' && <NovaModel />}
      {id === 'titan' && <TitanModel />}

      {/* On-Hover ONLY: Name, Current Task & Speed */}
      {isHovered && (
        <Html
          position={[0, 1.95, 0]}
          center
          distanceFactor={15}
          zIndexRange={[100, 0]}
        >
          <div className="pointer-events-none select-none rounded-xl px-3 py-2 bg-white text-slate-900 border border-slate-300 shadow-xl transition-all min-w-[160px] text-center">
            <div className="flex items-center justify-center gap-1.5 font-bold text-xs">
              <span
                className={`w-2 h-2 rounded-full ${
                  status === 'Moving'
                    ? 'bg-blue-600 animate-pulse'
                    : status === 'Ready' || status === 'Picking' || status === 'Scanning'
                    ? 'bg-emerald-500'
                    : 'bg-amber-500'
                }`}
              />
              <span className="text-sm font-extrabold">{name}</span>
              <span className="text-xs text-slate-500 font-semibold ml-1">
                {speed.toFixed(1)} m/s
              </span>
            </div>
            <div className="text-xs text-slate-600 font-medium mt-1">
              {robot.currentAction}
            </div>
            <div className="text-[10px] text-blue-600 font-semibold mt-0.5">
              Click to inspect
            </div>
          </div>
        </Html>
      )}
    </group>
  );
}

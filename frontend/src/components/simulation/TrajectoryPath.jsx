import React, { useMemo } from 'react';
import { Line } from '@react-three/drei';
import * as THREE from 'three';

export function TrajectoryPath({
  historyPoints = [],
  plannedPoints = [],
  color = '#2563eb',
  showWaypoints = true,
  showPlanned = true
}) {
  const historyVectors = useMemo(() => {
    if (!historyPoints || historyPoints.length < 2) return null;
    return historyPoints.map((pt) => [pt.x, 0.05, pt.z]);
  }, [historyPoints]);

  const plannedVectors = useMemo(() => {
    if (!plannedPoints || plannedPoints.length < 2) return null;
    return plannedPoints.map((pt) => [pt.x, 0.06, pt.z]);
  }, [plannedPoints]);

  return (
    <group>
      {/* Route Line */}
      {historyVectors && (
        <Line
          points={historyVectors}
          color={color}
          lineWidth={3}
          transparent
          opacity={0.8}
        />
      )}

      {/* Planned dashed line */}
      {showPlanned && plannedVectors && (
        <Line
          points={plannedVectors}
          color="#64748b"
          lineWidth={2}
          dashed
          dashSize={0.4}
          gapSize={0.2}
          transparent
          opacity={0.5}
        />
      )}

      {/* Waypoint Markers */}
      {showWaypoints &&
        plannedPoints?.map((wp, idx) => (
          <group key={`wp-${idx}`} position={[wp.x, 0.06, wp.z]}>
            <mesh rotation={[-Math.PI / 2, 0, 0]}>
              <ringGeometry args={[0.2, 0.28, 24]} />
              <meshBasicMaterial
                color={color}
                side={THREE.DoubleSide}
              />
            </mesh>
            <mesh position={[0, 0.02, 0]}>
              <sphereGeometry args={[0.08, 12, 12]} />
              <meshBasicMaterial color={color} />
            </mesh>
          </group>
        ))}
    </group>
  );
}

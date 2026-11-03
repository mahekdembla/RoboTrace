import React, { useState, useEffect } from 'react';
import { FleetContext } from './fleetContextDefinition';
import { robotService } from '../services/robotService';
import { MOCK_ROBOTS, WAREHOUSE_DESTINATIONS, MOCK_FLEET_SUMMARY } from '../data/mockRobots';
import { MOCK_MISSIONS, MOCK_TRAJECTORIES } from '../data/mockMissions';
import { MOCK_INCIDENTS, MOCK_SAFETY_RULES, ERROR_TAXONOMY } from '../data/mockIncidents';
import { MOCK_ANNOTATIONS, MOCK_WAREHOUSE_ZONES } from '../data/mockAnnotations';
import {
  MOCK_SUCCESS_METRICS,
  MOCK_ERROR_DISTRIBUTION,
  MOCK_AGENT_COMPARISON,
  MOCK_ANNOTATION_STATS,
  MOCK_THROUGHPUT_DATA,
  MOCK_BATTERY_DATA
} from '../data/mockTelemetry';

const INITIAL_TELEMETRY = {
  successMetrics: MOCK_SUCCESS_METRICS,
  errorDistribution: MOCK_ERROR_DISTRIBUTION,
  agentComparison: MOCK_AGENT_COMPARISON,
  annotationStats: MOCK_ANNOTATION_STATS,
  throughput: MOCK_THROUGHPUT_DATA,
  battery: MOCK_BATTERY_DATA,
  velocity: [
    { point: 'Start', Atlas: 0.0, Nova: 0.0, Titan: 0.0 },
    { point: 'Aisle Entry', Atlas: 1.2, Nova: 1.0, Titan: 0.8 },
    { point: 'Midpoint', Atlas: 1.4, Nova: 1.1, Titan: 1.6 },
    { point: 'Turn/Align', Atlas: 0.6, Nova: 0.5, Titan: 0.7 },
    { point: 'Target', Atlas: 0.0, Nova: 0.0, Titan: 0.0 }
  ]
};

export function FleetProvider({ children }) {
  const [robots, setRobots] = useState(MOCK_ROBOTS);
  const [destinations, setDestinations] = useState(WAREHOUSE_DESTINATIONS);
  const [missions, setMissions] = useState(MOCK_MISSIONS);
  const [selectedMissionId, setSelectedMissionId] = useState('MISSION-001');
  const [fleetSummary, setFleetSummary] = useState(MOCK_FLEET_SUMMARY);
  const [errors, setErrors] = useState(MOCK_INCIDENTS);
  const [safetyRules, setSafetyRules] = useState(MOCK_SAFETY_RULES);
  const [annotations, setAnnotations] = useState(MOCK_ANNOTATIONS);
  const [zones, setZones] = useState(MOCK_WAREHOUSE_ZONES);
  const [telemetry, setTelemetry] = useState(INITIAL_TELEMETRY);
  const [errorTaxonomy] = useState(ERROR_TAXONOMY);

  const [selectedRobotId, setSelectedRobotId] = useState('atlas');
  const [movementState, setMovementState] = useState('idle'); // 'idle' | 'running' | 'paused'
  const [movementSpeed, setMovementSpeed] = useState(1);
  const [cameraMode, setCameraMode] = useState('isometric');

  // Trajectory Step-by-Step Replay State (RoboTrace)
  const [selectedStepId, setSelectedStepId] = useState(3); // Default to Step 3 (the collision event on Atlas)
  const [replayPlaying, setReplayPlaying] = useState(false);

  // Load initial data
  useEffect(() => {
    async function loadData() {
      const [r, d, m, s, errs, rules, ann, z, tel] = await Promise.all([
        robotService.getAgents(),
        robotService.getDestinations(),
        robotService.getMissions(),
        robotService.getFleetSummary(),
        robotService.getErrors(),
        robotService.getSafetyRules(),
        robotService.getAnnotations(),
        robotService.getWarehouseZones(),
        robotService.getAnalytics()
      ]);
      setRobots(r);
      setDestinations(d);
      setMissions(m);
      setFleetSummary(s);
      setErrors(errs);
      setSafetyRules(rules);
      setAnnotations(ann);
      setZones(z);
      setTelemetry(tel);
    }
    loadData();
  }, []);

  // Animation ticker for physical robot movements
  useEffect(() => {
    if (movementState !== 'running') return;

    const interval = setInterval(() => {
      setRobots((prevRobots) =>
        prevRobots.map((robot) => {
          if (!robot.waypoints || robot.waypoints.length < 2) return robot;

          const currentPos = robot.position;
          const target = robot.targetCoords || robot.waypoints[robot.waypoints.length - 1];
          const dx = target.x - currentPos.x;
          const dz = target.z - currentPos.z;
          const dist = Math.sqrt(dx * dx + dz * dz);

          // If reached target, execute action
          if (dist < 0.15) {
            let actionText = 'Arrived at Destination';
            let statusText = 'Ready';
            if (robot.id === 'atlas') {
              actionText = 'Gripping & Picking Package';
              statusText = 'Picking';
            } else if (robot.id === 'nova') {
              actionText = 'Scanning Shelf Racks';
              statusText = 'Scanning';
            } else if (robot.id === 'titan') {
              actionText = 'Lowering Pallet Deck';
              statusText = 'Delivering';
            }

            return {
              ...robot,
              status: statusText,
              currentAction: actionText,
              speed: 0.0
            };
          }

          // Move step towards target
          const stepSize = 0.05 * movementSpeed;
          const ratio = Math.min(stepSize / dist, 1);
          const nextX = currentPos.x + dx * ratio;
          const nextZ = currentPos.z + dz * ratio;

          // Compute heading angle in degrees
          const headingDeg = Math.round((Math.atan2(dx, dz) * 180) / Math.PI);

          return {
            ...robot,
            status: 'Moving',
            currentAction: `Moving to ${robot.destination}`,
            speed: (1.2 * movementSpeed),
            position: { ...currentPos, x: nextX, z: nextZ },
            heading: headingDeg
          };
        })
      );
    }, 40);

    return () => clearInterval(interval);
  }, [movementState, movementSpeed]);

  // Automated Replay Stepper (RoboTrace Trajectory Replay)
  useEffect(() => {
    if (!replayPlaying) return;

    const currentAgentKey = (selectedRobotId || 'atlas').toUpperCase();
    const agentTrajectory = MOCK_TRAJECTORIES[currentAgentKey] || MOCK_TRAJECTORIES.ATLAS;

    const interval = setInterval(() => {
      setSelectedStepId((prev) => {
        if (prev >= agentTrajectory.length) {
          setReplayPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 1800);

    return () => clearInterval(interval);
  }, [replayPlaying, selectedRobotId]);

  const selectedRobot = robots.find((r) => r.id === selectedRobotId) || robots[0] || null;

  // Selected agent's trajectory events
  const currentAgentKey = (selectedRobotId || 'atlas').toUpperCase();
  const currentTrajectory = MOCK_TRAJECTORIES[currentAgentKey] || MOCK_TRAJECTORIES.ATLAS;
  const currentStep = currentTrajectory.find((s) => s.step_id === selectedStepId) || currentTrajectory[0];

  // Movement Controls
  const startMovement = () => {
    setMovementState('running');
    robotService.startMission(selectedMissionId);
  };

  const pauseMovement = () => {
    setMovementState('paused');
    robotService.pauseMission(selectedMissionId);
  };

  const resumeMovement = () => {
    setMovementState('running');
  };

  const resetMovement = () => {
    setMovementState('idle');
    robotService.resetMission(selectedMissionId);
    setRobots((prevRobots) =>
      prevRobots.map((robot) => {
        let actionDesc = 'Ready';
        if (robot.id === 'atlas') actionDesc = 'Arm in Home Position';
        if (robot.id === 'nova') actionDesc = 'Sensors in Standby';
        if (robot.id === 'titan') actionDesc = 'Platform Lowered';

        return {
          ...robot,
          position: { ...robot.startPosition },
          status: 'Ready',
          currentAction: actionDesc,
          speed: 0.0
        };
      })
    );
  };

  // Assign Destination to Robot
  const assignDestination = (robotId, destinationId) => {
    const dest = destinations.find((d) => d.id === destinationId);
    if (!dest) return;

    setRobots((prevRobots) =>
      prevRobots.map((robot) => {
        if (robot.id !== robotId) return robot;

        const currentPos = robot.position;
        // Generate clean orthogonal route via the central highway / crossway
        const newWaypoints = [
          { x: currentPos.x, y: 0, z: currentPos.z },
          { x: currentPos.x, y: 0, z: 0 },
          { x: dest.position.x, y: 0, z: 0 },
          { x: dest.position.x, y: 0, z: dest.position.z }
        ];

        return {
          ...robot,
          destination: dest.name,
          targetCoords: dest.position,
          waypoints: newWaypoints,
          status: 'Ready to Move',
          currentAction: `Assigned: ${dest.name}`
        };
      })
    );
  };

  // Trigger Deliberate Error Demonstration Scenario (design.md Section 11)
  const triggerDemoError = () => {
    setSelectedRobotId('atlas');
    setSelectedStepId(3);
    setRobots((prevRobots) =>
      prevRobots.map((r) => {
        if (r.id === 'atlas') {
          return {
            ...r,
            position: { x: -8.2, y: 0.35, z: -3.2 },
            status: 'Failed',
            speed: 0.0,
            currentAction: 'Chassis Collided with Shelf A-2 (ERR-201)'
          };
        }
        return r;
      })
    );
  };

  // Submit Human Annotation (design.md Section 4.G & 4.I)
  const submitAnnotation = async (annotationData) => {
    const newAnnotation = await robotService.submitAnnotation(annotationData);

    // Update error review status to REVIEWED
    setErrors((prev) =>
      prev.map((err) =>
        err.id === annotationData.error_id
          ? { ...err, status: 'REVIEWED', error_category: annotationData.final_category }
          : err
      )
    );

    // Append to annotations history
    setAnnotations((prev) => [newAnnotation, ...prev]);

    return newAnnotation;
  };

  // Emergency Stop
  const emergencyStop = (robotId) => {
    setMovementState('paused');
    setRobots((prevRobots) =>
      prevRobots.map((robot) => {
        if (!robotId || robot.id === robotId) {
          return {
            ...robot,
            status: 'Stopped',
            speed: 0.0,
            currentAction: 'Emergency Stop Engaged'
          };
        }
        return robot;
      })
    );
  };

  const clearAlert = (alertId) => {
    setErrors((prev) =>
      prev.map((inc) => (inc.id === alertId ? { ...inc, status: 'REVIEWED' } : inc))
    );
  };

  const value = {
    robots,
    selectedRobotId,
    setSelectedRobotId,
    selectedRobot,
    destinations,
    missions,
    selectedMissionId,
    setSelectedMissionId,
    fleetSummary,
    errors,
    incidents: errors,
    safetyRules,
    annotations,
    zones,
    telemetry,
    errorTaxonomy,
    currentTrajectory,
    selectedStepId,
    setSelectedStepId,
    currentStep,
    replayPlaying,
    setReplayPlaying,
    movementState,
    startMovement,
    pauseMovement,
    resumeMovement,
    resetMovement,
    movementSpeed,
    setMovementSpeed,
    assignDestination,
    triggerDemoError,
    submitAnnotation,
    emergencyStop,
    clearAlert,
    cameraMode,
    setCameraMode
  };

  return <FleetContext.Provider value={value}>{children}</FleetContext.Provider>;
}

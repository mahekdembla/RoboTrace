import React, { useState } from 'react';
import {
  MapPin,
  Play,
  Pause,
  RotateCcw,
  AlertOctagon,
  Layers,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { useFleet } from '../hooks/useFleet';
import { Warehouse3D } from '../components/simulation/Warehouse3D';
import { StatusBadge } from '../components/common/StatusBadge';
import { Link } from 'react-router-dom';

export function Simulation() {
  const {
    robots,
    selectedRobotId,
    setSelectedRobotId,
    selectedRobot,
    destinations,
    missions,
    selectedMissionId,
    setSelectedMissionId,
    movementState,
    startMovement,
    pauseMovement,
    resumeMovement,
    resetMovement,
    assignDestination,
    triggerDemoError,
    currentTrajectory,
    selectedStepId,
    setSelectedStepId
  } = useFleet();

  const [showRoutes, setShowRoutes] = useState(true);

  return (
    <div className="relative h-[calc(100vh-6.5rem)] w-full rounded-2xl overflow-hidden border border-slate-200 bg-white shadow-sm flex flex-col">
      {/* Top Floating Modern Control Dock */}
      <div className="p-3 bg-white/95 backdrop-blur-sm border-b border-slate-200 z-10 flex flex-wrap items-center justify-between gap-3 shrink-0">
        {/* Mission Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Mission:
          </span>
          <select
            value={selectedMissionId}
            onChange={(e) => setSelectedMissionId(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            {missions.map((m) => (
              <option key={m.id} value={m.id}>
                {m.id}: {m.title}
              </option>
            ))}
          </select>
        </div>

        {/* Robot Selection */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Agent:
          </span>
          <div className="flex items-center bg-slate-100 p-1 rounded-lg">
            {robots.map((r) => (
              <button
                key={r.id}
                onClick={() => setSelectedRobotId(r.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                  r.id === selectedRobotId
                    ? 'bg-white text-blue-700 shadow-sm border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: r.color }}
                />
                <span>{r.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Destination Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-blue-600" /> Destination:
          </span>
          <select
            value={destinations.find((d) => d.name === selectedRobot?.destination)?.id || ''}
            onChange={(e) => assignDestination(selectedRobotId, e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            {destinations.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>

        {/* Movement Controls (Start, Pause, Resume, Reset) & Demo Failure Trigger */}
        <div className="flex items-center gap-2">
          {movementState === 'idle' && (
            <button
              onClick={startMovement}
              className="btn-primary bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-3 py-1.5 rounded-lg"
            >
              <Play className="w-3.5 h-3.5 fill-current" /> Start
            </button>
          )}

          {movementState === 'running' && (
            <button
              onClick={pauseMovement}
              className="btn-primary bg-amber-500 hover:bg-amber-600 text-white text-xs px-3 py-1.5 rounded-lg"
            >
              <Pause className="w-3.5 h-3.5" /> Pause
            </button>
          )}

          {movementState === 'paused' && (
            <button
              onClick={resumeMovement}
              className="btn-primary bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1.5 rounded-lg"
            >
              <Play className="w-3.5 h-3.5 fill-current" /> Resume
            </button>
          )}

          <button
            onClick={resetMovement}
            className="btn-secondary text-xs px-2.5 py-1.5 rounded-lg"
            title="Reset positions"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset
          </button>

          {/* Trigger Deliberate Error Demonstration (Section 11) */}
          <button
            onClick={triggerDemoError}
            className="px-2.5 py-1.5 rounded-lg bg-amber-100 hover:bg-amber-200 text-amber-900 border border-amber-300 font-semibold text-xs flex items-center gap-1.5 transition-colors"
            title="Simulate Atlas Collision at Step 3"
          >
            <AlertOctagon className="w-3.5 h-3.5 text-amber-700" />
            Inject Fault
          </button>

          {/* Toggle Paths */}
          <button
            onClick={() => setShowRoutes(!showRoutes)}
            className={`text-xs px-2.5 py-1.5 rounded-lg border font-medium transition-colors ${
              showRoutes
                ? 'bg-blue-50 text-blue-700 border-blue-200'
                : 'bg-white text-slate-600 border-slate-200'
            }`}
          >
            Routes: {showRoutes ? 'On' : 'Off'}
          </button>
        </div>
      </div>

      {/* Main 3D Viewport with Floating Details Drawer */}
      <div className="flex-1 relative overflow-hidden">
        <Warehouse3D
          robots={robots}
          selectedRobotId={selectedRobotId}
          onSelectRobot={setSelectedRobotId}
          showTrajectories={showRoutes}
        />

        {/* Floating Robot Inspector Card */}
        {selectedRobot && (
          <div className="absolute top-4 right-4 z-10 w-80 bg-white/95 backdrop-blur-md rounded-xl border border-slate-200 p-4 shadow-lg">
            <div className="flex items-start justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <span
                  className="w-3.5 h-3.5 rounded-full"
                  style={{ backgroundColor: selectedRobot.color }}
                />
                <div>
                  <h3 className="font-bold text-base text-slate-900">
                    {selectedRobot.name}
                  </h3>
                  <span className="text-xs text-slate-500 font-medium">
                    {selectedRobot.type}
                  </span>
                </div>
              </div>
              <StatusBadge status={selectedRobot.status} size="xs" />
            </div>

            <div className="mt-3 space-y-3 text-xs">
              {/* Visible Action Status */}
              <div className={`p-2.5 rounded-lg border ${
                selectedRobot.status === 'Failed'
                  ? 'bg-rose-50 border-rose-200'
                  : 'bg-blue-50/70 border-blue-200/60'
              }`}>
                <span className={`font-semibold text-[10px] uppercase block tracking-wider ${
                  selectedRobot.status === 'Failed' ? 'text-rose-600' : 'text-blue-600'
                }`}>
                  {selectedRobot.status === 'Failed' ? 'Anomaly Detected' : 'Current Action'}
                </span>
                <span className="font-bold text-slate-900 text-xs">
                  {selectedRobot.currentAction}
                </span>
              </div>

              {/* Equipment Feature */}
              <div>
                <span className="text-slate-400 text-[10px] uppercase font-semibold block">
                  Built-In Equipment
                </span>
                <span className="text-slate-800 font-medium block mt-0.5">
                  {selectedRobot.equipment}
                </span>
              </div>

              {/* Destination & Payload */}
              <div className="bg-slate-50 p-2.5 rounded-lg space-y-1.5 border border-slate-100">
                <div className="flex items-center justify-between text-slate-600">
                  <span className="flex items-center gap-1 font-medium">
                    <MapPin className="w-3.5 h-3.5 text-blue-600" /> Destination:
                  </span>
                  <span className="font-semibold text-slate-800 truncate max-w-[130px]">
                    {selectedRobot.destination}
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span className="font-medium text-slate-500">
                    Payload:
                  </span>
                  <span className="font-semibold text-slate-800 truncate max-w-[150px]">
                    {selectedRobot.payload?.item || 'Empty'}
                  </span>
                </div>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-100 text-slate-600">
                <div>
                  <span className="text-slate-400 text-[10px] uppercase font-semibold block">
                    Speed
                  </span>
                  <span className="font-bold text-slate-900 text-sm">
                    {selectedRobot.speed?.toFixed(1) ?? '0.0'} m/s
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] uppercase font-semibold block">
                    Battery
                  </span>
                  <span className="font-bold text-emerald-600 text-sm">
                    {selectedRobot.battery}%
                  </span>
                </div>
              </div>

              {/* Quick Link to RoboTrace Trajectory Replay */}
              <div className="pt-2 border-t border-slate-100">
                <Link
                  to="/trajectories"
                  className="w-full flex items-center justify-center gap-1.5 py-1.5 text-xs font-semibold text-blue-600 hover:text-blue-700 bg-blue-50/70 hover:bg-blue-100/70 rounded-lg transition-colors"
                >
                  Inspect in Trajectory Replay <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Bottom Floating Step Preview Bar */}
        <div className="absolute bottom-4 left-4 right-4 md:right-96 z-10 bg-white/95 backdrop-blur-md rounded-xl border border-slate-200 p-3 shadow-md flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 overflow-x-auto">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider shrink-0 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-blue-600" /> Replay Steps:
            </span>
            <div className="flex items-center gap-1.5">
              {currentTrajectory.map((step) => (
                <button
                  key={step.step_id}
                  onClick={() => setSelectedStepId(step.step_id)}
                  className={`px-2.5 py-1 rounded text-xs font-semibold transition-all ${
                    step.step_id === selectedStepId
                      ? step.status === 'FAILED'
                        ? 'bg-rose-600 text-white'
                        : 'bg-blue-600 text-white shadow-sm'
                      : step.status === 'FAILED'
                      ? 'bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  Step {step.step_id}
                  {step.status === 'FAILED' && ' (!)'}
                </button>
              ))}
            </div>
          </div>

          <Link
            to="/trajectories"
            className="text-xs font-semibold text-blue-600 hover:underline shrink-0 flex items-center gap-1"
          >
            Full Audit <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}

import React from 'react';
import { Play, Pause, RotateCcw, MapPin } from 'lucide-react';
import { useFleet } from '../../hooks/useFleet';

export function MovementControls({ compact = false }) {
  const {
    robots,
    selectedRobotId,
    setSelectedRobotId,
    selectedRobot,
    destinations,
    movementState,
    startMovement,
    pauseMovement,
    resumeMovement,
    resetMovement,
    movementSpeed,
    setMovementSpeed,
    assignDestination
  } = useFleet();

  return (
    <div className={`card-pro p-3 sm:p-4 ${compact ? 'border-none shadow-none p-0' : ''}`}>
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: Robot Selection Tabs */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Robot:
          </span>
          <div className="flex items-center p-1 bg-slate-100 rounded-lg">
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
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: r.color }}
                />
                <span>{r.name}</span>
                <span className="text-[10px] text-slate-400 font-normal">
                  ({r.type})
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Center: Destination Selector */}
        <div className="flex items-center gap-2 flex-wrap">
          <label className="text-xs font-semibold text-slate-500 flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-blue-600" />
            Destination:
          </label>
          <select
            value={destinations.find((d) => d.name === selectedRobot?.destination)?.id || ''}
            onChange={(e) => assignDestination(selectedRobotId, e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-slate-800 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          >
            <option value="" disabled>Select destination...</option>
            {destinations.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>

        {/* Right: Movement Action Controls (Start, Pause, Resume, Reset) */}
        <div className="flex items-center gap-2 flex-wrap">
          {movementState === 'idle' && (
            <button
              onClick={startMovement}
              className="btn-primary bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs px-3.5 py-1.5 rounded-lg shadow-sm"
              title="Start moving robots to destinations"
            >
              <Play className="w-3.5 h-3.5 fill-current" /> Start
            </button>
          )}

          {movementState === 'running' && (
            <button
              onClick={pauseMovement}
              className="btn-primary bg-amber-500 hover:bg-amber-600 text-white font-medium text-xs px-3.5 py-1.5 rounded-lg shadow-sm"
              title="Pause robot movement"
            >
              <Pause className="w-3.5 h-3.5" /> Pause
            </button>
          )}

          {movementState === 'paused' && (
            <button
              onClick={resumeMovement}
              className="btn-primary bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-3.5 py-1.5 rounded-lg shadow-sm"
              title="Resume robot movement"
            >
              <Play className="w-3.5 h-3.5 fill-current" /> Resume
            </button>
          )}

          <button
            onClick={resetMovement}
            className="btn-secondary text-xs px-3 py-1.5 rounded-lg text-slate-700 hover:bg-slate-100"
            title="Reset robots back to starting stations"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset
          </button>

          {/* Speed Toggle (1x, 2x) */}
          <div className="flex items-center gap-1 border-l border-slate-200 pl-2">
            {[1, 2].map((sp) => (
              <button
                key={sp}
                onClick={() => setMovementSpeed(sp)}
                className={`px-2 py-1 rounded text-xs font-semibold ${
                  movementSpeed === sp
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                {sp}x
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

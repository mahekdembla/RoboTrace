import React from 'react';
import {
  Route,
  Navigation,
  Compass,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCcw,
  AlertTriangle,
  CheckCircle2,
  Eye,
  Brain,
  Zap,
  Target,
  ShieldAlert
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { useFleet } from '../hooks/useFleet';
import { Link } from 'react-router-dom';

export function Trajectories() {
  const {
    robots,
    selectedRobotId,
    setSelectedRobotId,
    selectedRobot,
    currentTrajectory,
    selectedStepId,
    setSelectedStepId,
    currentStep,
    replayPlaying,
    setReplayPlaying,
    telemetry
  } = useFleet();

  const velocityData = telemetry?.velocity || [];

  const handlePrevStep = () => {
    setSelectedStepId((prev) => Math.max(1, prev - 1));
  };

  const handleNextStep = () => {
    setSelectedStepId((prev) => Math.min(currentTrajectory?.length || 1, prev + 1));
  };

  const handleResetReplay = () => {
    setReplayPlaying(false);
    setSelectedStepId(1);
  };

  const isFailedStep = currentStep?.status === 'FAILED';

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header Card */}
      <div className="card-pro p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Route className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-bold text-slate-900">
                RoboTrace™ Trajectory Replay & Event Auditing
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Step-by-step audit of observations, decisions, actions, and outcomes for every discrete mission interval.
            </p>
          </div>

          {/* Robot Selector Buttons */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500">Agent:</span>
            <div className="flex items-center p-1 bg-slate-100 rounded-lg">
              {robots.map((r) => (
                <button
                  key={r.id}
                  onClick={() => {
                    setSelectedRobotId(r.id);
                    setSelectedStepId(1);
                  }}
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
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Step Scrubber & Playback Controls */}
        <div className="mt-5 pt-4 border-t border-slate-100 flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Controls: Play/Pause, Step Back, Step Forward, Reset */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setReplayPlaying(!replayPlaying)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-colors ${
                replayPlaying
                  ? 'bg-amber-500 hover:bg-amber-600 text-white'
                  : 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
              }`}
            >
              {replayPlaying ? (
                <>
                  <Pause className="w-4 h-4 fill-current" /> Pause Replay
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" /> Auto Replay
                </>
              )}
            </button>

            <button
              onClick={handlePrevStep}
              disabled={selectedStepId <= 1}
              className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
              title="Previous Step"
            >
              <SkipBack className="w-4 h-4" />
            </button>

            <button
              onClick={handleNextStep}
              disabled={selectedStepId >= (currentTrajectory?.length || 1)}
              className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
              title="Next Step"
            >
              <SkipForward className="w-4 h-4" />
            </button>

            <button
              onClick={handleResetReplay}
              className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-500 hover:text-slate-800"
              title="Reset to Step 1"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            <span className="text-xs font-mono font-semibold text-slate-600 ml-2">
              Step {selectedStepId} of {currentTrajectory?.length || 1}
            </span>
          </div>

          {/* Stepper Dots / Badges */}
          <div className="flex items-center gap-2 overflow-x-auto max-w-full pb-1">
            {(currentTrajectory || []).map((step) => {
              const isActive = step.step_id === selectedStepId;
              const isError = step.status === 'FAILED';

              return (
                <button
                  key={step.step_id}
                  onClick={() => setSelectedStepId(step.step_id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                    isActive
                      ? isError
                        ? 'bg-rose-600 text-white border-rose-600 shadow-sm ring-2 ring-rose-200'
                        : 'bg-blue-600 text-white border-blue-600 shadow-sm ring-2 ring-blue-200'
                      : isError
                      ? 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {isError ? (
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                  )}
                  <span>Step {step.step_id}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Event Audit Card (Observation, Decision, Action, Expected, Actual Outcome) */}
      <div
        className={`card-pro p-6 border-l-4 transition-all ${
          isFailedStep
            ? 'border-l-rose-600 bg-rose-50/15'
            : 'border-l-emerald-600 bg-emerald-50/10'
        }`}
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
          <div className="flex items-center gap-3">
            <span
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                isFailedStep
                  ? 'bg-rose-100 text-rose-700'
                  : 'bg-emerald-100 text-emerald-700'
              }`}
            >
              #{selectedStepId}
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base text-slate-900">
                  {currentStep?.action || 'Executing Movement'}
                </h3>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    isFailedStep
                      ? 'bg-rose-100 text-rose-800'
                      : 'bg-emerald-100 text-emerald-800'
                  }`}
                >
                  {currentStep?.status || 'SUCCESS'}
                </span>
              </div>
              <span className="text-xs text-slate-500 font-mono">
                Primitive: {currentStep?.action_primitive || 'MOVE'} | Timestamp: {currentStep?.timestamp || '08:30:00'}
              </span>
            </div>
          </div>

          {/* Quick link to AgentGuard if error detected */}
          {isFailedStep && (
            <Link
              to="/agentguard"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold shadow-sm transition-colors"
            >
              <ShieldAlert className="w-4 h-4" />
              View Detected Error in AgentGuard &rarr;
            </Link>
          )}
        </div>

        {/* 4 Pillars of Agent Decision: Observation, Reasoning, Expected Outcome, Actual Outcome */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
          {/* Box 1: Observation */}
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-blue-700 font-bold text-xs uppercase tracking-wider">
              <Eye className="w-4 h-4" />
              Observation (Sensor Feeds & Environment)
            </div>
            <p className="text-xs text-slate-700 leading-relaxed font-mono bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              {currentStep?.observation || 'No sensor anomalies reported.'}
            </p>
          </div>

          {/* Box 2: Decision Summary */}
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-indigo-700 font-bold text-xs uppercase tracking-wider">
              <Brain className="w-4 h-4" />
              Decision Summary (Planner Intent)
            </div>
            <p className="text-xs text-slate-700 leading-relaxed font-mono bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              {currentStep?.decision_summary || 'Trajectory optimal path generation.'}
            </p>
          </div>

          {/* Box 3: Expected Outcome */}
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-emerald-700 font-bold text-xs uppercase tracking-wider">
              <Target className="w-4 h-4" />
              Expected Outcome
            </div>
            <p className="text-xs text-slate-700 leading-relaxed font-mono bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              {currentStep?.expected_outcome || 'Agent reaches designated waypoint smoothly.'}
            </p>
          </div>

          {/* Box 4: Actual Outcome & Failure Detection */}
          <div
            className={`p-4 rounded-xl border shadow-sm space-y-2 ${
              isFailedStep
                ? 'bg-rose-50/40 border-rose-200'
                : 'bg-white border-slate-200/80'
            }`}
          >
            <div
              className={`flex items-center gap-2 font-bold text-xs uppercase tracking-wider ${
                isFailedStep ? 'text-rose-700' : 'text-slate-800'
              }`}
            >
              <Zap className="w-4 h-4" />
              Actual Outcome {isFailedStep && '(Execution Divergence)'}
            </div>
            <p
              className={`text-xs leading-relaxed font-mono p-2.5 rounded-lg border ${
                isFailedStep
                  ? 'bg-rose-100/60 border-rose-200 text-rose-950 font-semibold'
                  : 'bg-slate-50 border-slate-100 text-slate-700'
              }`}
            >
              {currentStep?.actual_outcome || 'Action succeeded within tolerances.'}
            </p>
            {currentStep?.error_detected && (
              <div className="flex items-center gap-1.5 text-xs text-rose-700 font-bold mt-1">
                <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                Error Flag: {currentStep.error_detected}
              </div>
            )}
          </div>
        </div>

        {/* Side-by-Side Planned vs Executed Coordinates */}
        <div className="mt-5 p-4 bg-slate-50 rounded-xl border border-slate-200/70">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-2">
            <Compass className="w-4 h-4 text-blue-600" />
            Trajectory Coordinate Comparison: Planned vs Executed
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
            <div className="p-2.5 bg-white rounded-lg border border-slate-200">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">
                Planned Waypoint
              </span>
              <span className="text-slate-900 font-bold">
                X: {(currentStep?.planned_coordinates?.x ?? currentStep?.coordinates?.x ?? currentStep?.position?.x ?? 0).toFixed(1)}m, 
                Z: {(currentStep?.planned_coordinates?.z ?? currentStep?.coordinates?.z ?? currentStep?.position?.z ?? 0).toFixed(1)}m
              </span>
              <span className="text-[11px] text-slate-500 block">Corridor Centerline</span>
            </div>
            <div
              className={`p-2.5 rounded-lg border ${
                isFailedStep
                  ? 'bg-rose-50 border-rose-300'
                  : 'bg-white border-slate-200'
              }`}
            >
              <span className="text-[10px] uppercase font-bold text-slate-400 block">
                Executed Waypoint
              </span>
              <span
                className={`font-bold ${
                  isFailedStep ? 'text-rose-700' : 'text-slate-900'
                }`}
              >
                X: {(currentStep?.coordinates?.x ?? currentStep?.position?.x ?? 0).toFixed(1)}m, 
                Z: {(currentStep?.coordinates?.z ?? currentStep?.position?.z ?? 0).toFixed(1)}m
              </span>
              <span
                className={`text-[11px] block ${
                  isFailedStep ? 'text-rose-600 font-semibold' : 'text-emerald-600'
                }`}
              >
                {isFailedStep
                  ? 'Deviation > 40cm (Collision Threshold Exceeded)'
                  : 'Within ±2cm tolerance'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Speed & Acceleration Profile Chart */}
      <div className="card-pro p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Navigation className="w-4 h-4 text-blue-600" />
              Travel Velocity Along Discrete Steps (m/s)
            </h3>
            <p className="text-xs text-slate-500">
              RoboTrace continuous velocity recording for {selectedRobot?.name || 'Agent'}
            </p>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={velocityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="point" stroke="#94a3b8" tick={{ fontSize: 12 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} unit=" m/s" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.5rem',
                  fontSize: '12px'
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Line
                type="monotone"
                dataKey="Atlas"
                name="Atlas (Picker)"
                stroke="#ea580c"
                strokeWidth={2.5}
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="Nova"
                name="Nova (Scanner)"
                stroke="#2563eb"
                strokeWidth={2.5}
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="Titan"
                name="Titan (Transporter)"
                stroke="#ca8a04"
                strokeWidth={2.5}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Step Sequence Table */}
      <div className="card-pro p-5">
        <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Route className="w-4 h-4 text-blue-600" />
          Full Trajectory Sequence for {selectedRobot?.name || 'Agent'}
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 uppercase text-[10px] font-semibold">
                <th className="py-2.5 px-3">Step</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Primitive</th>
                <th className="py-2.5 px-3">Action Description</th>
                <th className="py-2.5 px-3">Executed Coordinates</th>
                <th className="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {(currentTrajectory || []).map((step) => {
                const isSelected = step.step_id === selectedStepId;
                const isError = step.status === 'FAILED';

                return (
                  <tr
                    key={step.step_id}
                    onClick={() => setSelectedStepId(step.step_id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? isError
                          ? 'bg-rose-50/80 font-medium'
                          : 'bg-blue-50/80 font-medium'
                        : 'hover:bg-slate-50'
                    }`}
                  >
                    <td className="py-3 px-3 font-mono font-bold text-slate-900">
                      #{step.step_id}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-500">
                      {step.timestamp}
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-mono text-[10px]">
                        {step.action_primitive}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-900">
                      {step.action}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-600">
                      ({(step.coordinates?.x ?? step.position?.x ?? 0).toFixed(1)}, {(step.coordinates?.z ?? step.position?.z ?? 0).toFixed(1)})
                    </td>
                    <td className="py-3 px-3 text-right">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          isError
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-emerald-100 text-emerald-800'
                        }`}
                      >
                        {step.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

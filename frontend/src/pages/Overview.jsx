import React from 'react';
import {
  Activity,
  ShieldCheck,
  ArrowUpRight,
  Sparkles,
  AlertOctagon,
  CheckCircle2,
  FileCheck2,
  Play
} from 'lucide-react';
import { useFleet } from '../hooks/useFleet';
import { AgentCard } from '../components/common/AgentCard';
import { ErrorCard } from '../components/common/ErrorCard';
import { MovementControls } from '../components/common/MovementControls';
import { Warehouse3D } from '../components/simulation/Warehouse3D';
import { Link } from 'react-router-dom';

export function Overview() {
  const {
    robots,
    fleetSummary,
    errors,
    incidents,
    missions,
    selectedMissionId,
    setSelectedMissionId,
    selectedRobotId,
    setSelectedRobotId,
    clearAlert,
    triggerDemoError,
    annotations
  } = useFleet();

  const allErrors = errors || incidents || [];
  const activeAlerts = allErrors.filter((i) => i.status !== 'Resolved' && i.status !== 'REVIEWED');
  const pendingAnnotations = allErrors.filter((i) => i.status === 'PENDING_REVIEW').length;
  const currentMission = missions.find((m) => m.id === selectedMissionId) || missions[0];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Current Mission & Quick Workflow Bar */}
      <div className="card-pro p-4 bg-gradient-to-r from-blue-900 to-slate-900 text-white border-0 shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-blue-500/30 text-blue-200 border border-blue-400/30">
                Active Mission: {currentMission?.id || 'MISSION-001'}
              </span>
              <span className="text-xs text-slate-300 font-mono">
                {currentMission?.status || 'IN_PROGRESS'}
              </span>
            </div>
            <h2 className="text-lg font-bold text-white tracking-tight">
              {currentMission?.title || 'Autonomous Multi-Agent Pick & Transfer'}
            </h2>
            <p className="text-xs text-slate-300 max-w-2xl">
              {currentMission?.description ||
                'Executing coordinated package transport with Atlas, Nova, and Titan.'}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={selectedMissionId}
              onChange={(e) => setSelectedMissionId(e.target.value)}
              className="text-xs bg-slate-800/90 text-white border border-slate-700 rounded-lg px-3 py-1.5 font-medium focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              {missions.map((m) => (
                <option key={m.id} value={m.id} className="bg-slate-900 text-white">
                  {m.id}: {m.title}
                </option>
              ))}
            </select>

            <button
              onClick={triggerDemoError}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs shadow-sm transition-all"
              title="Simulates Section 11 failure scenario: Atlas collision at Step 3"
            >
              <AlertOctagon className="w-3.5 h-3.5" />
              Demo Injected Failure
            </button>
          </div>
        </div>
      </div>

      {/* 4 Clean Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Fleet Status */}
        <div className="card-pro p-4">
          <div className="flex items-center justify-between text-slate-500 mb-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider">Fleet Status</span>
            <Activity className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">
              {fleetSummary?.activeRobots ?? 3} Active
            </span>
            <span className="text-xs text-slate-500">of 3 Agents</span>
          </div>
          <div className="mt-2 text-xs text-slate-600 border-t border-slate-100 pt-2 flex items-center justify-between">
            <span>Atlas, Nova, Titan</span>
            <span className="text-emerald-600 font-semibold">Online & Tracked</span>
          </div>
        </div>

        {/* Card 2: Mission Success Rate */}
        <div className="card-pro p-4">
          <div className="flex items-center justify-between text-slate-500 mb-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider">Task Success Rate</span>
            <CheckCircle2 className="w-4 h-4 text-blue-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">
              {fleetSummary?.taskSuccessRate ?? 94.2}%
            </span>
            <span className="text-xs text-slate-500">Benchmark: 90%</span>
          </div>
          <div className="mt-2 text-xs text-slate-600 border-t border-slate-100 pt-2 flex items-center justify-between">
            <span>Step Execution</span>
            <span className="text-blue-600 font-semibold">+4.2% over target</span>
          </div>
        </div>

        {/* Card 3: AgentGuard Detected Errors */}
        <div className="card-pro p-4">
          <div className="flex items-center justify-between text-slate-500 mb-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider">AgentGuard Alerts</span>
            <ShieldCheck className="w-4 h-4 text-amber-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">
              {activeAlerts.length} Detected
            </span>
            <span className="text-xs text-slate-500">across 9 categories</span>
          </div>
          <div className="mt-2 text-xs text-slate-600 border-t border-slate-100 pt-2 flex items-center justify-between">
            <span>Safety Guard</span>
            <span className={activeAlerts.length > 0 ? "text-amber-600 font-semibold" : "text-emerald-600 font-semibold"}>
              {activeAlerts.length > 0 ? "Review Required" : "All Clear"}
            </span>
          </div>
        </div>

        {/* Card 4: Human Annotations Pending */}
        <div className="card-pro p-4">
          <div className="flex items-center justify-between text-slate-500 mb-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider">Human Annotations</span>
            <FileCheck2 className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">
              {pendingAnnotations} Pending
            </span>
            <span className="text-xs text-slate-500">({annotations.length} verified)</span>
          </div>
          <div className="mt-2 text-xs text-slate-600 border-t border-slate-100 pt-2 flex items-center justify-between">
            <span>Ground Truth Loop</span>
            <Link to="/annotations" className="text-indigo-600 font-semibold hover:underline">
              Open Review &rarr;
            </Link>
          </div>
        </div>
      </div>

      {/* Dual Core Pillars: RoboTrace & AgentGuard Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Pillar 1: RoboTrace Simulation & Replay */}
        <div className="card-pro p-4 border-l-4 border-l-blue-600 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                RoboTrace Core
              </span>
              <Link to="/trajectories" className="text-xs font-semibold text-blue-600 flex items-center gap-1 hover:underline">
                Replay Scrubbing <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </div>
            <h3 className="font-bold text-slate-900 text-sm">3D Warehouse & Step-by-Step Trajectory Recording</h3>
            <p className="text-xs text-slate-500 mt-1">
              Inspect observations, planner decisions, and motor executions at every discrete time step.
            </p>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-2">
            <Link to="/simulation" className="btn-primary text-xs px-3 py-1.5 rounded-lg flex items-center gap-1.5">
              <Play className="w-3.5 h-3.5 fill-current" /> Live 3D Simulation
            </Link>
            <Link to="/trajectories" className="btn-secondary text-xs px-3 py-1.5 rounded-lg">
              Scrub Trajectories
            </Link>
          </div>
        </div>

        {/* Pillar 2: AgentGuard Evaluation & Taxonomy */}
        <div className="card-pro p-4 border-l-4 border-l-amber-500 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-amber-600 bg-amber-50 px-2 py-0.5 rounded">
                AgentGuard Core
              </span>
              <Link to="/agentguard" className="text-xs font-semibold text-amber-600 flex items-center gap-1 hover:underline">
                Taxonomy Matrix <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Automated Decision Evaluation & 9-Category Taxonomy</h3>
            <p className="text-xs text-slate-500 mt-1">
              Catches perception, navigation, manipulation, and coordination anomalies with confidence scoring.
            </p>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-2">
            <Link to="/agentguard" className="btn-primary bg-amber-600 hover:bg-amber-700 text-white text-xs px-3 py-1.5 rounded-lg">
              View Safety Guard
            </Link>
            <Link to="/annotations" className="btn-secondary text-xs px-3 py-1.5 rounded-lg">
              Annotate Decisions
            </Link>
          </div>
        </div>
      </div>

      {/* Interactive Movement Controls Bar */}
      <MovementControls />

      {/* Main 3D Interactive Warehouse Viewport */}
      <div className="card-pro overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/60">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
              Live 3D Warehouse Floor
            </h2>
            <p className="text-xs text-slate-500">
              Click any robot to select it, or use the controls above to start and assign destinations
            </p>
          </div>
          <Link
            to="/simulation"
            className="btn-secondary text-xs px-3 py-1.5 text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
          >
            Open Full 3D Studio <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="h-[440px] relative">
          <Warehouse3D
            robots={robots}
            selectedRobotId={selectedRobotId}
            onSelectRobot={setSelectedRobotId}
            showTrajectories={true}
          />
        </div>
      </div>

      {/* The 3 Specialized Robots Roster */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Warehouse Robot Fleet</h2>
            <p className="text-xs text-slate-500">
              Atlas (Arm Picker), Nova (Shelf Scanner), and Titan (Pallet Transporter)
            </p>
          </div>
          <span className="text-xs font-medium text-slate-500">
            Click a card to focus
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {robots.map((robot) => (
            <AgentCard
              key={robot.id}
              robot={robot}
              isSelected={robot.id === selectedRobotId}
              onSelect={setSelectedRobotId}
            />
          ))}
        </div>
      </div>

      {/* Safety & Action Notices */}
      {allErrors.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Recent Safety & Detected Errors ({allErrors.length})
            </h2>
            <Link to="/agentguard" className="text-xs font-semibold text-blue-600 hover:underline">
              View AgentGuard Taxonomy &rarr;
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {allErrors.slice(0, 4).map((incident) => (
              <ErrorCard
                key={incident.id}
                incident={incident}
                onAcknowledge={clearAlert}
                onFocusAgent={setSelectedRobotId}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

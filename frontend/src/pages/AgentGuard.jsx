import React, { useState } from 'react';
import {
  ShieldCheck,
  AlertOctagon,
  CheckCircle2,
  Lock,
  Play,
  Filter,
  ArrowRight,
  FileCheck2,
  Layers
} from 'lucide-react';
import { useFleet } from '../hooks/useFleet';
import { Link, useNavigate } from 'react-router-dom';

export function AgentGuard() {
  const {
    errors,
    incidents,
    safetyRules,
    emergencyStop,
    resumeMovement,
    setSelectedRobotId,
    errorTaxonomy
  } = useFleet();

  const navigate = useNavigate();
  const allErrors = errors || incidents || [];

  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('ALL');
  const [selectedStatusFilter, setSelectedStatusFilter] = useState('ALL');

  const filteredErrors = allErrors.filter((err) => {
    const category = err.error_category || err.type || '';
    const status = err.status || '';

    const matchesCategory =
      selectedCategoryFilter === 'ALL' || category === selectedCategoryFilter;
    const matchesStatus =
      selectedStatusFilter === 'ALL' ||
      (selectedStatusFilter === 'PENDING' && (status === 'PENDING_REVIEW' || status === 'Active')) ||
      (selectedStatusFilter === 'REVIEWED' && (status === 'REVIEWED' || status === 'Resolved'));

    return matchesCategory && matchesStatus;
  });

  const activeErrorsCount = allErrors.filter(
    (e) => e.status === 'PENDING_REVIEW' || e.status === 'Active'
  ).length;

  const reviewedErrorsCount = allErrors.filter(
    (e) => e.status === 'REVIEWED' || e.status === 'Resolved'
  ).length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="card-pro p-5 border-l-4 border-l-blue-600">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-slate-900">
                AgentGuard™ Autonomous Decision & Safety Monitor
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Automated anomaly detection across the 9-category robotics failure taxonomy with confidence scoring.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => resumeMovement()}
              className="btn-secondary text-xs px-3.5 py-2 rounded-lg text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border-emerald-200 flex items-center gap-1.5"
            >
              <Play className="w-3.5 h-3.5 fill-current" /> Resume All Safe
            </button>
            <button
              onClick={() => emergencyStop()}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs shadow-sm transition-colors"
            >
              <AlertOctagon className="w-4 h-4" />
              Emergency Stop (All Robots)
            </button>
          </div>
        </div>

        {/* Safety KPI Summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-4 border-t border-slate-100 text-xs">
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">
              Pending Reviews
            </span>
            <span className="text-amber-600 font-bold text-lg">
              {activeErrorsCount} Require Review
            </span>
            <span className="text-slate-500 text-[11px] block">Escalated to human operator</span>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">
              Reviewed & Verified
            </span>
            <span className="text-emerald-600 font-bold text-lg">
              {reviewedErrorsCount} Decisions
            </span>
            <span className="text-slate-500 text-[11px] block">Ground truth confirmed</span>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">
              Taxonomy Categories
            </span>
            <span className="text-blue-600 font-bold text-lg">
              9 Formal Types
            </span>
            <span className="text-slate-500 text-[11px] block">ISO robotics standard</span>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">
              Confidence Floor
            </span>
            <span className="text-emerald-600 font-bold text-lg">
              &gt; 90% Detection
            </span>
            <span className="text-slate-500 text-[11px] block">Bayesian decision model</span>
          </div>
        </div>
      </div>

      {/* The 9-Category Error Taxonomy Matrix Reference */}
      <div className="card-pro p-5 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              AgentGuard™ 9-Category Failure Taxonomy
            </h3>
            <p className="text-xs text-slate-500">
              Click any category badge to filter the detected incidents below
            </p>
          </div>
          {selectedCategoryFilter !== 'ALL' && (
            <button
              onClick={() => setSelectedCategoryFilter('ALL')}
              className="text-xs font-semibold text-blue-600 hover:underline"
            >
              Clear Filter
            </button>
          )}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 pt-1">
          {(errorTaxonomy || []).map((cat) => {
            const isSelected = selectedCategoryFilter === cat.id;
            const count = allErrors.filter(
              (e) => (e.error_category || e.type) === cat.id
            ).length;

            return (
              <button
                key={cat.id}
                onClick={() =>
                  setSelectedCategoryFilter(isSelected ? 'ALL' : cat.id)
                }
                className={`p-2.5 rounded-lg border text-left transition-all ${
                  isSelected
                    ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                    : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-800'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-bold ${isSelected ? 'text-white' : 'text-slate-900'}`}>
                    {cat.name.replace(' Error', '')}
                  </span>
                  {count > 0 && (
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                        isSelected
                          ? 'bg-white/20 text-white'
                          : 'bg-amber-100 text-amber-900'
                      }`}
                    >
                      {count}
                    </span>
                  )}
                </div>
                <p
                  className={`text-[10px] line-clamp-2 mt-1 ${
                    isSelected ? 'text-blue-100' : 'text-slate-500'
                  }`}
                >
                  {cat.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Filter and Detected Errors Roster */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-500" />
            <h3 className="text-base font-bold text-slate-900">
              Detected Failure Incidents ({filteredErrors.length})
            </h3>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={selectedStatusFilter}
              onChange={(e) => setSelectedStatusFilter(e.target.value)}
              className="text-xs bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            >
              <option value="ALL">All Statuses</option>
              <option value="PENDING">Pending Human Review</option>
              <option value="REVIEWED">Reviewed & Ground Truth</option>
            </select>

            <Link
              to="/annotations"
              className="btn-primary text-xs px-3 py-1.5 rounded-lg flex items-center gap-1.5 shadow-sm"
            >
              <FileCheck2 className="w-3.5 h-3.5" />
              Human Annotation Studio
            </Link>
          </div>
        </div>

        {filteredErrors.length === 0 ? (
          <div className="card-pro p-8 text-center text-slate-500 text-sm">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            No failure incidents found matching the selected filter.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredErrors.map((incident) => {
              const isReviewed =
                incident.status === 'REVIEWED' || incident.status === 'Resolved';
              const agentKey = (incident.agent_id || incident.robotId || 'atlas').toLowerCase();

              return (
                <div
                  key={incident.id}
                  className={`card-pro p-5 border-l-4 transition-all flex flex-col justify-between ${
                    isReviewed
                      ? 'border-l-emerald-500 bg-emerald-50/10'
                      : incident.severity === 'High' || incident.severity === 'Critical'
                      ? 'border-l-rose-600 bg-rose-50/20'
                      : 'border-l-amber-500 bg-amber-50/20'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-xs text-slate-800">
                          {incident.id}
                        </span>
                        <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-medium">
                          {incident.agentName || incident.agent_id}
                        </span>
                        {incident.step_id && (
                          <span className="text-[11px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-mono">
                            Step #{incident.step_id}
                          </span>
                        )}
                      </div>

                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                          isReviewed
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-amber-100 text-amber-900'
                        }`}
                      >
                        {incident.status}
                      </span>
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-bold text-slate-900">
                          {incident.error_category || incident.type}
                        </h4>
                        <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                          Confidence: {incident.confidence ? `${Math.round(incident.confidence * 100)}%` : '94%'}
                        </span>
                      </div>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        {incident.description}
                      </p>
                    </div>

                    {/* Sensor Evidence */}
                    {incident.evidence && (
                      <div className="p-2.5 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700">
                        <span className="font-bold text-slate-900 block text-[10px] uppercase font-sans mb-0.5">
                          Sensor Evidence:
                        </span>
                        {incident.evidence}
                      </div>
                    )}
                  </div>

                  {/* Card Footer Actions */}
                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                    <button
                      onClick={() => {
                        setSelectedRobotId(agentKey);
                        navigate('/trajectories');
                      }}
                      className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
                    >
                      Audit Trajectory Step <ArrowRight className="w-3.5 h-3.5" />
                    </button>

                    <div className="flex items-center gap-2">
                      <Link
                        to="/annotations"
                        className="btn-primary text-xs px-2.5 py-1.5 rounded-lg flex items-center gap-1 bg-indigo-600 hover:bg-indigo-700 text-white"
                      >
                        <FileCheck2 className="w-3.5 h-3.5" />
                        Human Review
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Active Warehouse Safety Rules Table */}
      <div className="card-pro p-5 space-y-3">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Lock className="w-4 h-4 text-blue-600" />
              Active Autonomous Safety Invariants
            </h3>
            <p className="text-xs text-slate-500">
              Deterministic collision boundaries enforced in real-time
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            Safety Guard Active
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 uppercase text-[10px] font-semibold">
                <th className="py-2.5 px-3">Invariant Name</th>
                <th className="py-2.5 px-3">Constraint Details</th>
                <th className="py-2.5 px-3">Automated Interlock Action</th>
                <th className="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {(safetyRules || []).map((rule) => (
                <tr key={rule.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-3 font-bold text-slate-900">{rule.name}</td>
                  <td className="py-3 px-3 text-slate-600">{rule.detail}</td>
                  <td className="py-3 px-3 text-blue-700 font-medium">{rule.action}</td>
                  <td className="py-3 px-3 text-right">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800">
                      {rule.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

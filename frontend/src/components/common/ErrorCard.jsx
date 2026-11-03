import React from 'react';
import { AlertTriangle, CheckCircle2, MapPin, Clock, ArrowRight } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function ErrorCard({ incident, onAcknowledge, onFocusAgent }) {
  if (!incident) return null;

  const isResolved = incident.status === 'Resolved' || incident.status === 'REVIEWED';
  const categoryName = incident.error_category || incident.type || 'Error';
  const agentDisplayName = incident.agentName || incident.robotName || incident.agent_id || 'Robot';
  const targetRobotId = (incident.agent_id || incident.robotId || 'atlas').toLowerCase();
  const timeStr = incident.timestamp || incident.time || '08:30';

  return (
    <div
      className={`rounded-xl border p-4 transition-all ${
        isResolved
          ? 'bg-slate-50/60 border-slate-200'
          : incident.severity === 'Critical' || incident.severity === 'High'
          ? 'bg-rose-50/30 border-rose-200'
          : 'bg-amber-50/30 border-amber-200'
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-slate-200/60">
        <div className="flex items-center gap-2.5">
          {isResolved ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-xs text-slate-800">
                {incident.id}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-medium">
                {agentDisplayName}
              </span>
              {incident.step_id && (
                <span className="text-[11px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-mono">
                  Step {incident.step_id}
                </span>
              )}
            </div>
            <h4 className="text-sm font-bold text-slate-900 mt-0.5">
              {categoryName}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <StatusBadge status={incident.status} size="xs" />
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            {timeStr}
          </span>
        </div>
      </div>

      {/* Description */}
      <p className="mt-2.5 text-xs text-slate-600 leading-relaxed">
        {incident.description}
      </p>

      {/* Location & Action */}
      <div className="mt-3 p-2.5 rounded-lg bg-white border border-slate-200/80 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-1.5 text-slate-600">
          <MapPin className="w-3.5 h-3.5 text-blue-600" />
          <span className="font-medium text-slate-800">{incident.location}</span>
        </div>

        {incident.evidence && (
          <span className="text-slate-500 font-mono text-[10px] truncate max-w-xs">
            {incident.evidence}
          </span>
        )}
        {incident.recommendation && (
          <span className="text-blue-700 font-medium text-[11px]">
            {incident.recommendation}
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="mt-3 flex items-center justify-end gap-2">
        {onFocusAgent && (
          <button
            onClick={() => onFocusAgent(targetRobotId)}
            className="text-xs font-semibold px-3 py-1.5 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors flex items-center gap-1"
          >
            Locate in 3D <ArrowRight className="w-3.5 h-3.5" />
          </button>
        )}
        {!isResolved && onAcknowledge && (
          <button
            onClick={() => onAcknowledge(incident.id)}
            className="text-xs font-medium px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
          >
            Clear Alert
          </button>
        )}
      </div>
    </div>
  );
}

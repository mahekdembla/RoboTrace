import React from 'react';
import { Battery, Gauge, MapPin, Package } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function AgentCard({ robot, isSelected, onSelect }) {
  if (!robot) return null;

  const batteryColor =
    robot.battery > 50
      ? 'bg-emerald-500'
      : robot.battery > 25
      ? 'bg-amber-500'
      : 'bg-rose-500';

  return (
    <div
      onClick={() => onSelect && onSelect(robot.id)}
      className={`cursor-pointer rounded-xl p-4 transition-all duration-150 border text-left ${
        isSelected
          ? 'bg-blue-50/50 border-blue-600 shadow-sm ring-1 ring-blue-500/30'
          : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'
      }`}
    >
      {/* Top Header: Name + Badge */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2.5">
          <span
            className="w-3.5 h-3.5 rounded-full shrink-0 shadow-sm"
            style={{ backgroundColor: robot.color }}
          />
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-900">{robot.name}</h3>
              <span className="text-[11px] font-semibold text-slate-500 px-2 py-0.5 rounded-md bg-slate-100">
                {robot.type}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">{robot.tagline}</p>
          </div>
        </div>
        <StatusBadge status={robot.status} size="xs" />
      </div>

      {/* Visible Action Status Banner */}
      <div className="my-3 p-2.5 rounded-lg bg-slate-50 border border-slate-200/60 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
        <div className="text-xs">
          <span className="text-slate-500 block text-[10px] uppercase font-semibold tracking-wider">
            Current Action
          </span>
          <span className="font-semibold text-slate-800">{robot.currentAction}</span>
        </div>
      </div>

      {/* Key Metrics: Battery & Speed */}
      <div className="grid grid-cols-2 gap-3 py-2.5 border-y border-slate-100 text-xs">
        <div>
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="flex items-center gap-1 font-medium">
              <Battery className="w-3.5 h-3.5 text-slate-400" /> Battery
            </span>
            <span className="font-bold text-slate-800">{robot.battery}%</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div
              className={`h-full ${batteryColor}`}
              style={{ width: `${robot.battery}%` }}
            />
          </div>
        </div>

        <div className="flex items-center justify-between pl-3 border-l border-slate-100">
          <div>
            <span className="text-slate-400 text-[10px] uppercase font-semibold block">
              Speed
            </span>
            <span className="font-bold text-slate-800 text-sm">
              {robot.speed.toFixed(1)}{' '}
              <span className="text-xs font-normal text-slate-500">m/s</span>
            </span>
          </div>
          <Gauge className="w-4 h-4 text-slate-400" />
        </div>
      </div>

      {/* Destination & Payload */}
      <div className="mt-3 space-y-1.5 text-xs">
        <div className="flex items-center gap-1.5 text-slate-700">
          <MapPin className="w-3.5 h-3.5 text-blue-600 shrink-0" />
          <span className="text-slate-500">Heading to:</span>
          <span className="font-semibold text-slate-800 truncate">
            {robot.destination}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-slate-600">
          <Package className="w-3.5 h-3.5 text-amber-600 shrink-0" />
          <span className="truncate">{robot.payload.item}</span>
          <span className="text-slate-400 text-[11px]">({robot.payload.weight})</span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
        <span className="text-slate-400 font-mono text-[11px]">
          Pos: [{robot.position.x.toFixed(1)}, {robot.position.z.toFixed(1)}]
        </span>
        <span
          className={`font-semibold text-[11px] ${
            isSelected ? 'text-blue-600' : 'text-slate-500'
          }`}
        >
          {isSelected ? '✓ Selected' : 'Click to select'}
        </span>
      </div>
    </div>
  );
}

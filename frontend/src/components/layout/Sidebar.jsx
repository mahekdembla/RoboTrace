import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Box,
  Route,
  ShieldCheck,
  MapPin,
  BarChart3,
  Bot,
  Activity
} from 'lucide-react';
import { useFleet } from '../../hooks/useFleet';

const NAV_ITEMS = [
  {
    name: 'Overview',
    path: '/',
    icon: LayoutDashboard,
    hint: 'Fleet Dashboard'
  },
  {
    name: 'Simulation',
    path: '/simulation',
    icon: Box,
    hint: '3D Warehouse Studio'
  },
  {
    name: 'Trajectories',
    path: '/trajectories',
    icon: Route,
    hint: 'Routes & Waypoints'
  },
  {
    name: 'AgentGuard',
    path: '/agentguard',
    icon: ShieldCheck,
    hint: 'Safety & Incidents'
  },
  {
    name: 'Annotations',
    path: '/annotations',
    icon: MapPin,
    hint: 'Facility Notes & Zones'
  },
  {
    name: 'Analytics',
    path: '/analytics',
    icon: BarChart3,
    hint: 'Performance Reports'
  }
];

export function Sidebar({ collapsed }) {
  const { robots, incidents } = useFleet();
  const alertList = incidents || [];
  const activeAlerts = alertList.filter((i) => i.status !== 'Resolved' && i.status !== 'REVIEWED').length;
  const robotList = robots || [];

  return (
    <aside
      className={`relative z-20 flex flex-col bg-white border-r border-slate-200 transition-all duration-200 ease-in-out shrink-0 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center px-4 border-b border-slate-200">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-blue-600 text-white shadow-sm shrink-0">
            <Bot className="w-5 h-5" />
          </div>

          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-base text-slate-900 tracking-tight flex items-center gap-1">
                RoboTrace <span className="text-blue-600 text-xs px-1.5 py-0.5 rounded bg-blue-50 font-bold">3D</span>
              </span>
              <span className="text-xs text-slate-500 font-medium">
                Warehouse Robotics
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          {!collapsed ? 'Navigation' : 'Menu'}
        </div>

        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                } ${collapsed ? 'justify-center px-0' : ''}`
              }
            >
              <Icon className="w-5 h-5 shrink-0" />
              {!collapsed && (
                <div className="flex-1 truncate flex items-center justify-between">
                  <span>{item.name}</span>
                  {item.name === 'AgentGuard' && activeAlerts > 0 && (
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-800">
                      {activeAlerts}
                    </span>
                  )}
                </div>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Live Fleet Snapshot in Footer */}
      {!collapsed && (
        <div className="p-3 mx-3 mb-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-600">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-emerald-500" /> Active Robots
            </span>
            <span className="text-slate-400 font-normal">3 Online</span>
          </div>

          <div className="space-y-1.5 pt-1 text-xs">
            {robotList.map((r) => (
              <div key={r.id} className="flex items-center justify-between text-slate-700">
                <span className="flex items-center gap-1.5 font-medium">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: r.color }}
                  />
                  {r.name}
                </span>
                <span className="text-[11px] text-slate-500 truncate max-w-[100px]">
                  {r.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
}

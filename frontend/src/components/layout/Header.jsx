import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Menu,
  Clock,
  ShieldCheck,
  AlertOctagon,
  Play,
  Pause
} from 'lucide-react';
import { useFleet } from '../../hooks/useFleet';

export function Header({ collapsed, setCollapsed }) {
  const location = useLocation();
  const {
    movementState,
    startMovement,
    pauseMovement,
    resumeMovement,
    emergencyStop,
    incidents
  } = useFleet();

  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const getPageInfo = () => {
    switch (location.pathname) {
      case '/':
      case '/overview':
        return { title: 'Fleet Overview', desc: 'Real-time monitoring and movement control for Atlas, Nova, and Titan' };
      case '/simulation':
        return { title: '3D Warehouse Studio', desc: 'Interactive 3D view with robot animations and destination controls' };
      case '/trajectories':
        return { title: 'Routes & Waypoints', desc: 'Inspect travel paths, waypoints, and accuracy metrics' };
      case '/agentguard':
        return { title: 'Safety & Incident Guard', desc: 'Safety rules, collision alerts, and emergency stop controls' };
      case '/annotations':
        return { title: 'Facility Map & Marked Zones', desc: 'Warehouse work zones, walking aisles, and operator notes' };
      case '/analytics':
        return { title: 'Performance Reports', desc: 'Packages moved today, battery usage, and warehouse zone activity' };
      default:
        return { title: 'RoboTrace 3D', desc: 'Warehouse Robotics Dashboard' };
    }
  };

  const { title, desc } = getPageInfo();
  const alertList = incidents || [];
  const activeAlerts = alertList.filter((i) => i.status !== 'Resolved' && i.status !== 'REVIEWED').length;

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between gap-4 z-10 shrink-0">
      {/* Left: Sidebar toggle + Page Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          title="Toggle Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight leading-tight">
            {title}
          </h1>
          <p className="hidden md:block text-xs text-slate-500">
            {desc}
          </p>
        </div>
      </div>

      {/* Right: Quick Controls, Clock & Emergency Stop */}
      <div className="flex items-center gap-3">
        {/* Movement Quick Toggle */}
        <div className="hidden sm:flex items-center gap-2">
          {movementState === 'running' ? (
            <button
              onClick={pauseMovement}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-100 transition-colors"
            >
              <Pause className="w-3.5 h-3.5" /> Pause Fleet
            </button>
          ) : (
            <button
              onClick={movementState === 'paused' ? resumeMovement : startMovement}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition-colors"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              {movementState === 'paused' ? 'Resume Fleet' : 'Start Fleet'}
            </button>
          )}
        </div>

        {/* Safety Status Pill */}
        <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs font-medium text-slate-700">
          <ShieldCheck className={`w-4 h-4 ${activeAlerts > 0 ? 'text-amber-500' : 'text-emerald-500'}`} />
          <span>{activeAlerts > 0 ? `${activeAlerts} Notice` : 'Safety OK'}</span>
        </div>

        {/* Live Facility Clock */}
        <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 font-medium px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-200">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{currentTime || '08:00 AM'}</span>
        </div>

        {/* Emergency Stop All Robots */}
        <button
          onClick={() => emergencyStop()}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs transition-colors shadow-sm"
          title="Instantly stop all robots"
        >
          <AlertOctagon className="w-4 h-4" />
          <span className="hidden sm:inline">Emergency Stop</span>
        </button>
      </div>
    </header>
  );
}

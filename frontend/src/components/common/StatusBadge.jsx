import React from 'react';

export function StatusBadge({ status, size = 'sm' }) {
  const getStyle = () => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'ready':
      case 'picking':
      case 'scanning':
      case 'operational':
      case 'resolved':
      case 'safe & clear':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'moving':
      case 'in transit':
      case 'moving to':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'warning':
      case 'delivering':
      case 'in progress':
      case 'monitoring':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'error':
      case 'stopped':
      case 'critical':
      case 'action required':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getDot = () => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'ready':
      case 'picking':
      case 'scanning':
      case 'operational':
      case 'resolved':
      case 'safe & clear':
        return 'bg-emerald-500';
      case 'moving':
      case 'in transit':
        return 'bg-blue-600 animate-pulse';
      case 'warning':
      case 'delivering':
      case 'in progress':
      case 'monitoring':
        return 'bg-amber-500';
      case 'error':
      case 'stopped':
      case 'critical':
        return 'bg-rose-500';
      default:
        return 'bg-slate-400';
    }
  };

  const sizeClass = size === 'xs' ? 'text-[11px] px-2 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium border ${getStyle()} ${sizeClass}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${getDot()}`} />
      <span className="capitalize">{status || 'Ready'}</span>
    </span>
  );
}

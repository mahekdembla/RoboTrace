import React from 'react';
import {
  BarChart3,
  TrendingUp,
  Download,
  Users,
  FileCheck2,
  Layers
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { useFleet } from '../hooks/useFleet';

export function Analytics() {
  const { telemetry, fleetSummary, annotations } = useFleet();

  const successMetrics = telemetry?.successMetrics || [
    { name: 'Completed Tasks', count: 18, color: '#10b981' },
    { name: 'Failed Tasks', count: 3, color: '#ef4444' }
  ];

  const errorDistribution = telemetry?.errorDistribution || [
    { category: 'Perception', count: 2 },
    { category: 'Navigation', count: 4 },
    { category: 'Planning', count: 3 },
    { category: 'Manipulation', count: 2 },
    { category: 'Collision', count: 3 },
    { category: 'Execution', count: 1 },
    { category: 'Recovery', count: 1 },
    { category: 'Task Completion', count: 2 },
    { category: 'Coordination', count: 1 }
  ];

  const agentComparison = telemetry?.agentComparison || [
    { agent: 'Atlas (Picker)', completedTasks: 6, errorsDetected: 3, successRate: 67 },
    { agent: 'Nova (Scanner)', completedTasks: 8, errorsDetected: 1, successRate: 89 },
    { agent: 'Titan (Transporter)', completedTasks: 7, errorsDetected: 1, successRate: 88 }
  ];

  const annotationStats = telemetry?.annotationStats || {
    totalReviewed: 6,
    acceptedByReviewer: 5,
    correctedByReviewer: 1,
    agreementRate: 83.3,
    averageReviewTimeSec: 42
  };

  const agreementData = [
    { name: 'AI Suggestion Accepted', value: annotationStats.acceptedByReviewer, color: '#10b981' },
    { name: 'Category Corrected', value: annotationStats.correctedByReviewer, color: '#f59e0b' }
  ];

  const handleExportReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      fleetSummary,
      annotationStats,
      agentComparison,
      errorTaxonomyDistribution: errorDistribution,
      totalAnnotations: annotations.length
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `robotrace_analytics_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header Card */}
      <div className="card-pro p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-bold text-slate-900">
                RoboTrace & AgentGuard Analytics & Performance
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Multi-agent reliability evaluation, 9-category error distributions, and human-in-the-loop agreement benchmarks.
            </p>
          </div>

          <button
            onClick={handleExportReport}
            className="btn-secondary text-xs px-3.5 py-2 flex items-center gap-1.5 font-semibold text-slate-700 bg-white hover:bg-slate-50 shadow-sm border border-slate-200"
          >
            <Download className="w-3.5 h-3.5 text-blue-600" /> Export JSON Audit Report
          </button>
        </div>

        {/* 4 KPI Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-4 border-t border-slate-100 text-xs">
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">
              Fleet Task Success
            </span>
            <span className="text-emerald-600 font-bold text-lg">
              {fleetSummary?.taskSuccessRate ?? 94.2}%
            </span>
            <span className="text-slate-500 text-[11px] block">18 of 21 tasks passed</span>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">
              Human-AI Agreement
            </span>
            <span className="text-blue-600 font-bold text-lg">
              {annotationStats.agreementRate}%
            </span>
            <span className="text-slate-500 text-[11px] block">5/6 Suggestions accepted</span>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">
              Taxonomy Breadth
            </span>
            <span className="text-slate-900 font-bold text-lg">
              9 Failure Classes
            </span>
            <span className="text-slate-500 text-[11px] block">Full coverage active</span>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">
              Avg Review Latency
            </span>
            <span className="text-indigo-600 font-bold text-lg">
              {annotationStats.averageReviewTimeSec}s
            </span>
            <span className="text-slate-500 text-[11px] block">Per human decision</span>
          </div>
        </div>
      </div>

      {/* Chart Row 1: Task Success Rate & Human Agreement Rate */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Task Success Rate Breakdown (7 cols) */}
        <div className="lg:col-span-7 card-pro p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-600" />
                  Task Success vs Flagged Interventions
                </h3>
                <p className="text-xs text-slate-500">
                  Total autonomous warehouse tasks successfully executed vs halted by AgentGuard
                </p>
              </div>
            </div>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={successMetrics} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                  <YAxis
                    dataKey="name"
                    type="category"
                    stroke="#64748b"
                    tick={{ fontSize: 11 }}
                    width={140}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      borderColor: '#e2e8f0',
                      borderRadius: '0.5rem',
                      fontSize: '12px'
                    }}
                  />
                  <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                    {(successMetrics || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-2 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
            <span>Overall Fleet Reliability Benchmark</span>
            <span className="font-bold text-emerald-600">Target &gt; 90.0% (Exceeded)</span>
          </div>
        </div>

        {/* Right: Human vs AI Annotation Agreement Donut (5 cols) */}
        <div className="lg:col-span-5 card-pro p-5 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2 mb-1">
              <FileCheck2 className="w-4 h-4 text-indigo-600" />
              Human-AI Annotation Agreement
            </h3>
            <p className="text-xs text-slate-500 mb-2">
              Rate at which human operators accepted AgentGuard AI error classifications
            </p>

            <div className="h-52 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={agreementData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {(agreementData || []).map((entry, index) => (
                      <Cell key={`pie-cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      borderColor: '#e2e8f0',
                      borderRadius: '0.5rem',
                      fontSize: '12px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-100 text-xs">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-slate-600">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                Accepted AI Suggestion
              </span>
              <span className="font-bold text-slate-900">83.3% (5)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-slate-600">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                Corrected by Operator
              </span>
              <span className="font-bold text-slate-900">16.7% (1)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Row 2: Error Distribution across the 9 Taxonomy Categories */}
      <div className="card-pro p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              Error Distribution Across 9-Category Taxonomy
            </h3>
            <p className="text-xs text-slate-500">
              Aggregated incident frequencies classified by the formal AgentGuard taxonomy
            </p>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={errorDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="category"
                stroke="#64748b"
                tick={{ fontSize: 10 }}
                interval={0}
                angle={-15}
                textAnchor="end"
                height={50}
              />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.5rem',
                  fontSize: '12px'
                }}
              />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Detected Errors" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart Row 3: Agent Comparison Matrix */}
      <div className="card-pro p-5 space-y-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-600" />
            Agent Reliability Comparison Matrix
          </h3>
          <p className="text-xs text-slate-500">
            Performance comparison across Atlas (Arm Picker), Nova (Shelf Scanner), and Titan (Pallet Transporter)
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          {/* Grouped Bar Chart (7 cols) */}
          <div className="lg:col-span-7 h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={agentComparison}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="agent" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    borderColor: '#e2e8f0',
                    borderRadius: '0.5rem',
                    fontSize: '12px'
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar
                  dataKey="completedTasks"
                  fill="#10b981"
                  radius={[4, 4, 0, 0]}
                  name="Tasks Completed"
                />
                <Bar
                  dataKey="errorsDetected"
                  fill="#ef4444"
                  radius={[4, 4, 0, 0]}
                  name="Errors Detected"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Agent Metrics Table (5 cols) */}
          <div className="lg:col-span-5 bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-3">
            <span className="text-[10px] uppercase font-bold text-slate-500 block">
              Agent Success Rates
            </span>

            {(agentComparison || []).map((item, idx) => (
              <div
                key={idx}
                className="p-2.5 bg-white rounded-lg border border-slate-200/80 flex items-center justify-between text-xs"
              >
                <div>
                  <h4 className="font-bold text-slate-900">{item.agent}</h4>
                  <span className="text-[11px] text-slate-500">
                    {item.completedTasks} completed / {item.errorsDetected} flagged
                  </span>
                </div>
                <div className="text-right">
                  <span
                    className={`font-bold text-sm block ${
                      item.successRate >= 80 ? 'text-emerald-600' : 'text-amber-600'
                    }`}
                  >
                    {item.successRate}%
                  </span>
                  <span className="text-[10px] text-slate-400">Success Rate</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

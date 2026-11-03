import React, { useState } from 'react';
import {
  FileCheck2,
  CheckCircle2,
  AlertTriangle,
  Send,
  ShieldCheck,
  Check,
  RotateCcw
} from 'lucide-react';
import { useFleet } from '../hooks/useFleet';
import { Link } from 'react-router-dom';

export function Annotations() {
  const {
    errors,
    incidents,
    annotations,
    submitAnnotation,
    errorTaxonomy
  } = useFleet();

  const allErrors = errors || incidents || [];
  const pendingErrors = allErrors.filter(
    (e) => e.status === 'PENDING_REVIEW' || e.status === 'Active'
  );

  // Selected error to review
  const [selectedErrorId, setSelectedErrorId] = useState(
    pendingErrors[0]?.id || allErrors[0]?.id || ''
  );
  const selectedError =
    allErrors.find((e) => e.id === selectedErrorId) || allErrors[0];

  // Form State
  const [decisionType, setDecisionType] = useState('ACCEPT'); // 'ACCEPT' | 'CORRECT'
  const [finalCategory, setFinalCategory] = useState(
    selectedError?.error_category || selectedError?.suggested_category || 'Collision Error'
  );
  const [reviewerId, setReviewerId] = useState('Operator-Lead-102');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [submissionSuccess, setSubmissionSuccess] = useState(false);
  const [reviewTimestamp] = useState(() => new Date().toLocaleTimeString());

  // When selected error changes, initialize defaults
  const handleSelectError = (err) => {
    setSelectedErrorId(err.id);
    const cat = err.error_category || err.suggested_category || 'Collision Error';
    setFinalCategory(cat);
    setDecisionType('ACCEPT');
    setReviewerNotes('');
    setSubmissionSuccess(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedError) return;

    await submitAnnotation({
      error_id: selectedError.id,
      mission_id: selectedError.mission_id || 'MISSION-001',
      step_id: selectedError.step_id || 1,
      suggested_category: selectedError.suggested_category || selectedError.error_category || 'Collision Error',
      final_category: decisionType === 'ACCEPT'
        ? (selectedError.suggested_category || selectedError.error_category)
        : finalCategory,
      decision: decisionType === 'ACCEPT' ? 'ACCEPTED' : 'CORRECTED',
      reviewer_id: reviewerId,
      notes: reviewerNotes || (decisionType === 'ACCEPT' ? 'Confirmed AgentGuard AI assessment.' : 'Reclassified based on telemetry verification.')
    });

    setSubmissionSuccess(true);
    setTimeout(() => {
      setSubmissionSuccess(false);
      // Select next pending error if available
      const remaining = allErrors.filter((item) => item.id !== selectedError.id && item.status === 'PENDING_REVIEW');
      if (remaining.length > 0) {
        handleSelectError(remaining[0]);
      }
    }, 1500);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="card-pro p-5 border-l-4 border-l-indigo-600">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <FileCheck2 className="w-6 h-6 text-indigo-600" />
              <h2 className="text-xl font-bold text-slate-900">
                AgentGuard™ Human-in-the-Loop Annotation Studio
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Verify AI-detected decision anomalies, accept or reclassify failure taxonomy categories, and record operator ground truth.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="px-3 py-1.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 font-semibold">
              {pendingErrors.length} Pending Review
            </span>
            <span className="px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold">
              {annotations.length} Verified Annotations
            </span>
          </div>
        </div>
      </div>

      {/* Main Two-Column Workflow: Pending Queue on Left, Decision Form on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Error Selection Queue (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              Detected Errors Awaiting Review
            </h3>
            <span className="text-xs text-slate-500">
              {allErrors.length} Total Incidents
            </span>
          </div>

          <div className="space-y-2.5 max-h-[620px] overflow-y-auto pr-1">
            {allErrors.map((err) => {
              const isSelected = err.id === selectedError?.id;
              const isReviewed = err.status === 'REVIEWED' || err.status === 'Resolved';

              return (
                <div
                  key={err.id}
                  onClick={() => handleSelectError(err)}
                  className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-indigo-50/60 border-indigo-400 shadow-sm ring-1 ring-indigo-300'
                      : isReviewed
                      ? 'bg-slate-50/70 border-slate-200 opacity-75 hover:opacity-100'
                      : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-xs'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-xs text-slate-900">
                        {err.id}
                      </span>
                      <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-semibold">
                        {err.agentName || err.agent_id}
                      </span>
                      {err.step_id && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-mono">
                          Step #{err.step_id}
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
                      {err.status}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-slate-900 mt-2">
                    {err.error_category || err.type}
                  </h4>
                  <p className="text-[11px] text-slate-600 line-clamp-2 mt-0.5">
                    {err.description}
                  </p>

                  <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>Mission: {err.mission_id || 'MISSION-001'}</span>
                    <span className="text-indigo-600 font-bold">
                      Confidence: {err.confidence ? `${Math.round(err.confidence * 100)}%` : '94%'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Ground Truth Annotation Form (7 cols) */}
        <div className="lg:col-span-7">
          {selectedError ? (
            <div className="card-pro p-6 space-y-5 border-2 border-indigo-200 bg-white">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600">
                    Decision Verification Form
                  </span>
                  <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    Reviewing {selectedError.id} ({selectedError.agentName || selectedError.agent_id})
                  </h3>
                </div>

                <Link
                  to="/trajectories"
                  className="text-xs font-semibold text-blue-600 hover:underline flex items-center gap-1"
                >
                  View Step #{selectedError.step_id || 1} in Trajectories &rarr;
                </Link>
              </div>

              {/* Error Summary Card */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-600">AgentGuard AI Suggestion:</span>
                  <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold text-xs">
                    {selectedError.suggested_category || selectedError.error_category}
                  </span>
                </div>
                <p className="text-xs text-slate-700">
                  {selectedError.description}
                </p>
                {selectedError.evidence && (
                  <div className="mt-2 pt-2 border-t border-slate-200/60 font-mono text-[11px] text-slate-600">
                    <span className="font-sans font-bold text-slate-800 block text-[10px] uppercase">
                      Sensor Evidence:
                    </span>
                    {selectedError.evidence}
                  </div>
                )}
              </div>

              {/* Form Controls */}
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Decision Radio Choice */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Human Reviewer Decision
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => {
                        setDecisionType('ACCEPT');
                        setFinalCategory(selectedError.suggested_category || selectedError.error_category);
                      }}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        decisionType === 'ACCEPT'
                          ? 'bg-emerald-50 border-emerald-500 text-emerald-900 ring-2 ring-emerald-200'
                          : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      <div className="flex items-center gap-2 font-bold text-xs">
                        <Check className="w-4 h-4 text-emerald-600" />
                        Accept AI Suggestion
                      </div>
                      <span className="text-[11px] text-slate-500 block mt-1">
                        Confirm {selectedError.suggested_category || selectedError.error_category}
                      </span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setDecisionType('CORRECT')}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        decisionType === 'CORRECT'
                          ? 'bg-amber-50 border-amber-500 text-amber-900 ring-2 ring-amber-200'
                          : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      <div className="flex items-center gap-2 font-bold text-xs">
                        <RotateCcw className="w-4 h-4 text-amber-600" />
                        Correct Error Category
                      </div>
                      <span className="text-[11px] text-slate-500 block mt-1">
                        Reclassify to a different taxonomy type
                      </span>
                    </button>
                  </div>
                </div>

                {/* Final Category Dropdown */}
                {decisionType === 'CORRECT' && (
                  <div className="p-3.5 bg-amber-50/50 rounded-xl border border-amber-200 space-y-2">
                    <label className="block text-xs font-bold text-amber-900">
                      Select Correct Taxonomy Category (9 Standards):
                    </label>
                    <select
                      value={finalCategory}
                      onChange={(e) => setFinalCategory(e.target.value)}
                      className="w-full text-xs bg-white border border-slate-300 rounded-lg p-2.5 font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-amber-500"
                    >
                      {(errorTaxonomy || []).map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.name} — {cat.description}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Operator Identity & Notes */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Reviewer Operator ID
                    </label>
                    <input
                      type="text"
                      required
                      value={reviewerId}
                      onChange={(e) => setReviewerId(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Review Timestamp
                    </label>
                    <input
                      type="text"
                      disabled
                      value={reviewTimestamp}
                      className="w-full px-3 py-2 rounded-lg bg-slate-100 border border-slate-200 text-xs font-mono text-slate-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Auditor Notes & Root Cause Analysis
                  </label>
                  <textarea
                    rows={3}
                    value={reviewerNotes}
                    onChange={(e) => setReviewerNotes(e.target.value)}
                    placeholder="e.g. Confirmed post collision during step 3 avoidance pathing. Sensor clear."
                    className="w-full px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  />
                </div>

                {submissionSuccess && (
                  <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-semibold flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    Ground truth annotation successfully saved and synchronized to Analytics!
                  </div>
                )}

                <button
                  type="submit"
                  className="w-full btn-primary bg-indigo-600 hover:bg-indigo-700 text-white text-xs py-2.5 rounded-lg font-bold flex items-center justify-center gap-2 shadow-sm"
                >
                  <Send className="w-4 h-4" />
                  Submit Human Ground Truth Annotation
                </button>
              </form>
            </div>
          ) : (
            <div className="card-pro p-12 text-center text-slate-500">
              Select an error from the queue to start review.
            </div>
          )}
        </div>
      </div>

      {/* Historical Ground Truth Annotations Log */}
      <div className="card-pro p-5 space-y-3">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              Verified Ground Truth Dataset ({(annotations || []).length})
            </h3>
            <p className="text-xs text-slate-500">
              Formal audit records verified by certified operations engineers
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 uppercase text-[10px] font-semibold">
                <th className="py-2.5 px-3">Annotation ID</th>
                <th className="py-2.5 px-3">Target Error</th>
                <th className="py-2.5 px-3">AI Suggestion</th>
                <th className="py-2.5 px-3">Final Ground Truth</th>
                <th className="py-2.5 px-3">Decision</th>
                <th className="py-2.5 px-3">Reviewer</th>
                <th className="py-2.5 px-3">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {(annotations || []).map((ann) => (
                <tr key={ann.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-3 font-mono font-bold text-slate-900">
                    {ann.id}
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-600">
                    {ann.error_id}
                  </td>
                  <td className="py-3 px-3 text-slate-500">
                    {ann.suggested_category}
                  </td>
                  <td className="py-3 px-3 font-bold text-indigo-700">
                    {ann.final_category}
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        ann.decision === 'ACCEPTED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {ann.decision}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-600">
                    {ann.reviewer_id}
                  </td>
                  <td className="py-3 px-3 text-slate-600 max-w-xs truncate">
                    {ann.notes}
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

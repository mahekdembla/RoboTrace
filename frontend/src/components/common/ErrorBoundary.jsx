import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
          <div className="card-pro p-8 max-w-lg w-full text-center space-y-4 border-rose-200 bg-white shadow-xl">
            <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">
              Something went wrong
            </h2>
            <p className="text-xs text-slate-600 font-mono bg-slate-100 p-3 rounded-lg text-left overflow-x-auto">
              {this.state.error?.message || 'Unknown UI Error'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.href = '/';
              }}
              className="btn-primary w-full py-2.5 rounded-lg flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-4 h-4" /> Return to Fleet Overview
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}


import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { FleetProvider } from './context/FleetContext';
import { MainLayout } from './components/layout/MainLayout';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import {
  Overview,
  Simulation,
  Trajectories,
  AgentGuard,
  Annotations,
  Analytics
} from './pages';

export default function App() {
  return (
    <ErrorBoundary>
      <FleetProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Overview />} />
              <Route path="overview" element={<Navigate to="/" replace />} />
              <Route path="simulation" element={<Simulation />} />
              <Route path="trajectories" element={<Trajectories />} />
              <Route path="agentguard" element={<AgentGuard />} />
              <Route path="annotations" element={<Annotations />} />
              <Route path="analytics" element={<Analytics />} />
              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </FleetProvider>
    </ErrorBoundary>
  );
}

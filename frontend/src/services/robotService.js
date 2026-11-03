/**
 * API Service Layer conforming to design.md Section 7 API Contract
 * Attempts live REST/WebSocket connection to FastAPI backend (default: http://localhost:8000),
 * falling back gracefully to mock data when backend is not running.
 */

import { MOCK_ROBOTS, WAREHOUSE_DESTINATIONS, MOCK_FLEET_SUMMARY } from '../data/mockRobots';
import { MOCK_MISSIONS, MOCK_TRAJECTORIES } from '../data/mockMissions';
import { MOCK_INCIDENTS, MOCK_SAFETY_RULES, ERROR_TAXONOMY } from '../data/mockIncidents';
import { MOCK_ANNOTATIONS, MOCK_WAREHOUSE_ZONES } from '../data/mockAnnotations';
import {
  MOCK_SUCCESS_METRICS,
  MOCK_ERROR_DISTRIBUTION,
  MOCK_AGENT_COMPARISON,
  MOCK_ANNOTATION_STATS,
  MOCK_THROUGHPUT_DATA,
  MOCK_BATTERY_DATA
} from '../data/mockTelemetry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
const BACKEND_ENABLED = import.meta.env.VITE_ENABLE_BACKEND === 'true';

async function safeFetch(endpoint, options = {}, fallbackData) {
  if (!BACKEND_ENABLED || !API_BASE) {
    return Promise.resolve(fallbackData);
  }
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch {
    // Graceful fallback to mock data when backend is offline
    return fallbackData;
  }
}

export const robotService = {
  // GET /api/agents
  async getAgents() {
    return safeFetch('/api/agents', {}, [...MOCK_ROBOTS]);
  },

  // GET /api/missions
  async getMissions() {
    return safeFetch('/api/missions', {}, [...MOCK_MISSIONS]);
  },

  // POST /api/missions
  async createMission(missionData) {
    const newMission = {
      id: `MISSION-${Date.now().toString().slice(-3)}`,
      status: 'Ready',
      startTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
      ...missionData
    };
    return safeFetch('/api/missions', {
      method: 'POST',
      body: JSON.stringify(missionData)
    }, newMission);
  },

  // POST /api/missions/{id}/start
  async startMission(missionId) {
    return safeFetch(`/api/missions/${missionId}/start`, { method: 'POST' }, { status: 'STARTED', missionId });
  },

  // POST /api/missions/{id}/pause
  async pauseMission(missionId) {
    return safeFetch(`/api/missions/${missionId}/pause`, { method: 'POST' }, { status: 'PAUSED', missionId });
  },

  // POST /api/missions/{id}/reset
  async resetMission(missionId) {
    return safeFetch(`/api/missions/${missionId}/reset`, { method: 'POST' }, { status: 'RESET', missionId });
  },

  // GET /api/missions/{id}/trajectory
  async getTrajectory(missionId, agentId = 'ATLAS') {
    const normalizedAgent = agentId.toUpperCase();
    const fallback = MOCK_TRAJECTORIES[normalizedAgent] || MOCK_TRAJECTORIES.ATLAS;
    return safeFetch(`/api/missions/${missionId}/trajectory?agent_id=${normalizedAgent}`, {}, fallback);
  },

  // GET /api/errors
  async getErrors() {
    return safeFetch('/api/errors', {}, [...MOCK_INCIDENTS]);
  },

  // POST /api/annotations
  async submitAnnotation(annotationData) {
    const saved = {
      id: `ANN-${Date.now().toString().slice(-3)}`,
      timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19),
      status: 'REVIEWED',
      ...annotationData
    };
    return safeFetch('/api/annotations', {
      method: 'POST',
      body: JSON.stringify(annotationData)
    }, saved);
  },

  // GET /api/analytics
  async getAnalytics() {
    const fallback = {
      successMetrics: MOCK_SUCCESS_METRICS,
      errorDistribution: MOCK_ERROR_DISTRIBUTION,
      agentComparison: MOCK_AGENT_COMPARISON,
      annotationStats: MOCK_ANNOTATION_STATS,
      throughput: MOCK_THROUGHPUT_DATA,
      battery: MOCK_BATTERY_DATA
    };
    return safeFetch('/api/analytics', {}, fallback);
  },

  // Local helper getters
  async getDestinations() {
    return Promise.resolve([...WAREHOUSE_DESTINATIONS]);
  },

  async getSafetyRules() {
    return Promise.resolve([...MOCK_SAFETY_RULES]);
  },

  async getWarehouseZones() {
    return Promise.resolve([...MOCK_WAREHOUSE_ZONES]);
  },

  async getErrorTaxonomy() {
    return Promise.resolve([...ERROR_TAXONOMY]);
  },

  async getAnnotations() {
    return Promise.resolve([...MOCK_ANNOTATIONS]);
  },

  async getFleetSummary() {
    return Promise.resolve({ ...MOCK_FLEET_SUMMARY });
  }
};

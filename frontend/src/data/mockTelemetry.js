/**
 * Analytics and Evaluation Metrics according to design.md Section 4.H & 4.J
 */

export const MOCK_SUCCESS_METRICS = [
  { name: 'Completed Tasks', count: 18, color: '#10b981' },
  { name: 'Failed / Flagged Tasks', count: 3, color: '#ef4444' }
];

export const MOCK_ERROR_DISTRIBUTION = [
  { category: 'Perception Error', count: 2, color: '#6366f1' },
  { category: 'Navigation Error', count: 4, color: '#3b82f6' },
  { category: 'Planning Error', count: 3, color: '#0ea5e9' },
  { category: 'Manipulation Error', count: 2, color: '#f59e0b' },
  { category: 'Collision Error', count: 3, color: '#ef4444' },
  { category: 'Execution Error', count: 1, color: '#ec4899' },
  { category: 'Recovery Error', count: 1, color: '#8b5cf6' },
  { category: 'Task Completion Error', count: 2, color: '#f97316' },
  { category: 'Coordination Error', count: 1, color: '#14b8a6' }
];

export const MOCK_AGENT_COMPARISON = [
  { agent: 'ATLAS (Picker)', completedTasks: 6, errorsDetected: 3, collisionCount: 1, successRate: 67 },
  { agent: 'NOVA (Scanner)', completedTasks: 8, errorsDetected: 1, collisionCount: 0, successRate: 89 },
  { agent: 'TITAN (Transporter)', completedTasks: 7, errorsDetected: 1, collisionCount: 0, successRate: 88 }
];

export const MOCK_ANNOTATION_STATS = {
  totalReviewed: 6,
  acceptedByReviewer: 5,
  correctedByReviewer: 1,
  agreementRate: 83.3,
  averageReviewTimeSec: 42
};

export const MOCK_THROUGHPUT_DATA = [
  { time: '08:00', packagesMoved: 35, target: 30 },
  { time: '09:00', packagesMoved: 48, target: 45 },
  { time: '10:00', packagesMoved: 55, target: 50 },
  { time: '11:00', packagesMoved: 62, target: 55 },
  { time: '12:00', packagesMoved: 40, target: 40 },
  { time: '13:00', packagesMoved: 58, target: 55 },
  { time: '14:00', packagesMoved: 68, target: 60 },
  { time: '15:00', packagesMoved: 64, target: 60 },
  { time: '16:00', packagesMoved: 72, target: 65 }
];

export const MOCK_BATTERY_DATA = [
  { time: '08:00', Atlas: 100, Nova: 100, Titan: 100 },
  { time: '10:00', Atlas: 94, Nova: 91, Titan: 89 },
  { time: '12:00', Atlas: 89, Nova: 84, Titan: 78 },
  { time: '14:00', Atlas: 88, Nova: 76, Titan: 64 }
];

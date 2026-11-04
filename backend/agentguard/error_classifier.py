"""RoboTrace 3D — AgentGuard Error Classifier.

Deterministic rule-based error classification system mapping physical discrepancies,
state divergence, and protocol violations into standard AgentGuard categories:
1. PERCEPTION
2. NAVIGATION
3. PLANNING
4. MANIPULATION
5. COLLISION
6. EXECUTION
7. RECOVERY
8. TASK_COMPLETION
9. COORDINATION

No external AI or LLM APIs are used.
"""

from enum import Enum
from typing import Any, Dict, Optional, Tuple


class ErrorCategory(str, Enum):
    PERCEPTION = "PERCEPTION"
    NAVIGATION = "NAVIGATION"
    PLANNING = "PLANNING"
    MANIPULATION = "MANIPULATION"
    COLLISION = "COLLISION"
    EXECUTION = "EXECUTION"
    RECOVERY = "RECOVERY"
    TASK_COMPLETION = "TASK_COMPLETION"
    COORDINATION = "COORDINATION"


class ErrorSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorClassifier:
    """Classifies detected simulation anomalies into error categories and severities."""

    @staticmethod
    def classify(rule_id: str, context: Optional[Dict[str, Any]] = None) -> Tuple[ErrorCategory, ErrorSeverity]:
        """Map specific rule violation to category and severity level."""
        context = context or {}

        # 1. Collision Rules
        if rule_id.startswith("COLLISION_"):
            return (ErrorCategory.COLLISION, ErrorSeverity.HIGH)

        # 2. False Completion / Task Verification Rules
        if rule_id in ("TASK_FALSE_COMPLETION", "UNDELIVERED_PACKAGE_REPORTED_COMPLETE", "INSPECTION_UNVERIFIED"):
            return (ErrorCategory.TASK_COMPLETION, ErrorSeverity.HIGH)

        # 3. Manipulation Rules
        if rule_id in ("PICKUP_FAILED", "PLACEMENT_MISMATCH", "DROPPED_PACKAGE", "GRASP_SLIPPAGE"):
            return (ErrorCategory.MANIPULATION, ErrorSeverity.HIGH)

        # 4. Navigation Rules
        if rule_id in ("OFF_PATH", "ROUTE_BLOCKED", "WAYPOINT_TIMEOUT", "INVALID_ROUTE"):
            return (ErrorCategory.NAVIGATION, ErrorSeverity.MEDIUM)

        # 5. Perception Rules
        if rule_id in ("SENSOR_MISREAD", "BARCODE_SCAN_FAILURE", "OBJECT_DETECTION_MISMATCH"):
            return (ErrorCategory.PERCEPTION, ErrorSeverity.MEDIUM)

        # 6. Planning Rules
        if rule_id in ("INCOMPATIBLE_TASK_ASSIGNED", "UNREACHABLE_GOAL", "PRIORITY_INVERSION"):
            return (ErrorCategory.PLANNING, ErrorSeverity.HIGH)

        # 7. Recovery Rules
        if rule_id in ("FAILED_RECOVERY", "RECOVERY_TIMEOUT", "RETRY_LIMIT_EXCEEDED"):
            return (ErrorCategory.RECOVERY, ErrorSeverity.HIGH)

        # 8. Execution Rules
        if rule_id in ("REPEATED_UNNECESSARY_ACTION", "ACTION_TIMEOUT", "EXECUTION_HALTED"):
            return (ErrorCategory.EXECUTION, ErrorSeverity.MEDIUM)

        # 9. Coordination Rules
        if rule_id in ("SPATIAL_CONFLICT", "CORRIDOR_DEADLOCK", "SIMULTANEOUS_STATION_ACCESS"):
            return (ErrorCategory.COORDINATION, ErrorSeverity.HIGH)

        # Default fallback
        return (ErrorCategory.EXECUTION, ErrorSeverity.MEDIUM)


"""RoboTrace 3D — Mission Task Scheduler.

Responsible for:
- Receiving and validating mission tasks.
- Prioritizing tasks by urgency/priority level.
- Mapping task types to compatible agents (ATLAS, NOVA, TITAN).
- Spatial conflict prevention (preventing simultaneous access to same pickup/delivery station).
- Managing task execution lifecycle with the AgentManager and PyBullet simulation.
- Tracking task statuses and handling execution failures cleanly.
"""

from dataclasses import dataclass, field
import heapq
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from agents.agent_manager import AgentManager, AgentTask
from engine.simulation import WarehouseSimulation

logger = logging.getLogger("robotrace.task_scheduler")


@dataclass(order=True)
class PrioritizedTask:
    """Task wrapper ordered by priority (lower priority number = executed first)."""
    priority: int
    task_id: str = field(compare=False)
    task: AgentTask = field(compare=False)


class TaskScheduler:
    """Coordinates multi-robot mission task dispatching and spatial deconfliction."""

    def __init__(self, agent_manager: AgentManager, simulation: WarehouseSimulation):
        self.agent_manager = agent_manager
        self.simulation = simulation
        self._pending_tasks: List[PrioritizedTask] = []
        self._active_tasks: Dict[str, AgentTask] = {}
        self._completed_tasks: List[AgentTask] = []
        self._failed_tasks: List[AgentTask] = []

        # Spatial reservation locks: station_id or coord -> agent_id
        self._station_reservations: Dict[str, str] = {}

    # -----------------------------------------------------------------------
    # Task Submission & Validation
    # -----------------------------------------------------------------------

    def submit_task(
        self,
        task_id: str,
        task_type: str,
        priority: int = 1,
        payload: Optional[Dict[str, Any]] = None,
    ) -> AgentTask:
        """Submit a mission task to the priority queue after validation."""
        valid_types = {
            "TASK_PACKAGE_DELIVERY", "PACKAGE_DELIVERY",
            "TASK_INVENTORY_INSPECTION", "INVENTORY_INSPECTION",
            "TASK_MATERIAL_TRANSPORT", "MATERIAL_TRANSPORT",
        }
        if task_type.upper() not in valid_types:
            raise ValueError(
                f"Invalid task type '{task_type}'. Valid mission task types: {sorted(valid_types)}"
            )

        task = AgentTask(task_id=task_id, task_type=task_type.upper(), priority=priority, payload=payload)
        heapq.heappush(self._pending_tasks, PrioritizedTask(priority=priority, task_id=task_id, task=task))
        logger.info("Submitted task %s (%s, priority %d)", task_id, task_type, priority)
        return task

    # -----------------------------------------------------------------------
    # Dispatching with Shared-Space Conflict Prevention
    # -----------------------------------------------------------------------

    def find_compatible_agent(self, task_type: str) -> Optional[str]:
        """Find an idle agent capable of handling this task type."""
        for agent in self.agent_manager.get_all_agents():
            if agent.status in ["IDLE", "COMPLETED"]:
                if self.agent_manager.validate_task_compatibility(agent.agent_id, task_type):
                    return agent.agent_id
        return None

    def check_spatial_conflict(self, task: AgentTask) -> bool:
        """Check if target station or dropzone is already reserved by another active robot."""
        payload = task.payload
        target_station = payload.get("station_id") or payload.get("delivery_station") or payload.get("destination_id")
        if target_station and target_station in self._station_reservations:
            logger.info("Spatial conflict: Station %s is reserved by %s.", target_station, self._station_reservations[target_station])
            return True
        return False

    def reserve_spatial_zone(self, task: AgentTask, agent_id: str) -> None:
        """Lock destination station for the assigned robot."""
        payload = task.payload
        target_station = payload.get("station_id") or payload.get("delivery_station") or payload.get("destination_id")
        if target_station:
            self._station_reservations[target_station] = agent_id

    def release_spatial_zone(self, task: AgentTask) -> None:
        """Release destination reservation upon task completion or failure."""
        payload = task.payload
        target_station = payload.get("station_id") or payload.get("delivery_station") or payload.get("destination_id")
        if target_station:
            self._station_reservations.pop(target_station, None)

    def dispatch_next(self) -> Optional[Dict[str, Any]]:
        """Dispatch highest priority pending task without spatial conflicts to an available agent."""
        if not self._pending_tasks:
            return None

        # Inspect tasks in priority order
        deferred: List[PrioritizedTask] = []
        dispatched_result: Optional[Dict[str, Any]] = None

        while self._pending_tasks:
            p_task = heapq.heappop(self._pending_tasks)
            task = p_task.task

            # Check spatial conflict
            if self.check_spatial_conflict(task):
                deferred.append(p_task)
                continue

            # Find compatible idle agent
            agent_id = self.find_compatible_agent(task.task_type)
            if agent_id is None:
                # Agent busy or not available yet
                deferred.append(p_task)
                continue

            # Assign task
            self.reserve_spatial_zone(task, agent_id)
            self.agent_manager.assign_task(agent_id, task)
            self._active_tasks[task.task_id] = task

            # Execute task
            result = self.agent_manager.execute_assigned_task(agent_id)
            self.release_spatial_zone(task)
            self._active_tasks.pop(task.task_id, None)

            if result.get("success", False):
                self._completed_tasks.append(task)
            else:
                self._failed_tasks.append(task)

            dispatched_result = {
                "task_id": task.task_id,
                "agent_id": agent_id,
                "success": result.get("success", False),
                "result": result,
            }
            break

        # Re-insert any deferred tasks back into priority queue
        for item in deferred:
            heapq.heappush(self._pending_tasks, item)

        return dispatched_result

    def dispatch_all(self) -> List[Dict[str, Any]]:
        """Execute all queued tasks sequentially until priority queue is exhausted."""
        results = []
        while self._pending_tasks:
            res = self.dispatch_next()
            if res is None:
                break
            results.append(res)
        return results

    def get_queue_status(self) -> Dict[str, Any]:
        """Return overview of scheduler queue and task statuses."""
        return {
            "pending_count": len(self._pending_tasks),
            "active_count": len(self._active_tasks),
            "completed_count": len(self._completed_tasks),
            "failed_count": len(self._failed_tasks),
            "reserved_stations": self._station_reservations,
        }


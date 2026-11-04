"""RoboTrace 3D — Agent Manager.

Coordinates all registered autonomous robots:
- Registers ATLAS, NOVA, and TITAN.
- Enforces capability matching to prevent incompatible task assignments.
- Manages agent lifecycle statuses (IDLE, ASSIGNED, MOVING, WORKING, COMPLETED, FAILED, PAUSED).
- Tracks task execution progress, success, and failures.
- Interfaces with the physics simulation and navigation system.
"""

from enum import Enum
import logging
from typing import Any, Dict, List, Optional, Union

from agents.atlas import AtlasAgent
from agents.nova import NovaAgent
from agents.titan import TitanAgent
from engine.navigation import WaypointNavigator
from engine.simulation import WarehouseSimulation

logger = logging.getLogger("robotrace.agent_manager")


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    MOVING = "MOVING"
    WORKING = "WORKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class AgentTask:
    """Task specification dispatched to an agent."""

    def __init__(
        self,
        task_id: str,
        task_type: str,
        priority: int = 1,
        payload: Optional[Dict[str, Any]] = None,
    ):
        self.task_id = task_id
        self.task_type = task_type  # TASK_PACKAGE_DELIVERY, TASK_INVENTORY_INSPECTION, TASK_MATERIAL_TRANSPORT
        self.priority = priority
        self.payload = payload or {}
        self.status = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
        self.assigned_agent_id: Optional[str] = None
        self.error_message: Optional[str] = None
        self.result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.task_id,
            "type": self.task_type,
            "priority": self.priority,
            "status": self.status,
            "assigned_agent": self.assigned_agent_id,
            "payload": self.payload,
            "error": self.error_message,
        }


class AgentManager:
    """Central registry and coordinator for warehouse robot agents."""

    # Explicit capability mapping preventing incompatible task assignments
    CAPABILITIES: Dict[str, List[str]] = {
        "ATLAS": ["TASK_PACKAGE_DELIVERY", "PACKAGE_DELIVERY", "DELIVERY"],
        "NOVA": ["TASK_INVENTORY_INSPECTION", "INVENTORY_INSPECTION", "INSPECTION"],
        "TITAN": ["TASK_MATERIAL_TRANSPORT", "MATERIAL_TRANSPORT", "TRANSPORT"],
    }

    def __init__(self, simulation: Optional[WarehouseSimulation] = None):
        self.simulation = simulation
        self.navigator = WaypointNavigator()
        self.agents: Dict[str, Union[AtlasAgent, NovaAgent, TitanAgent]] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []

        # Automatically register the 3 standard agents
        self.register_agent(AtlasAgent())
        self.register_agent(NovaAgent())
        self.register_agent(TitanAgent())

    def register_agent(self, agent: Union[AtlasAgent, NovaAgent, TitanAgent]) -> None:
        """Register a new or custom robotic agent."""
        self.agents[agent.agent_id] = agent
        logger.info("Registered agent %s (%s)", agent.agent_id, agent.role)

    def get_agent(self, agent_id: str) -> Optional[Union[AtlasAgent, NovaAgent, TitanAgent]]:
        """Retrieve agent by ID."""
        return self.agents.get(agent_id.upper())

    def get_all_agents(self) -> List[Union[AtlasAgent, NovaAgent, TitanAgent]]:
        """Return list of all registered agents."""
        return list(self.agents.values())

    def get_agent_states(self) -> List[Dict[str, Any]]:
        """Get states for all agents using simulation as source of truth."""
        return [agent.get_state(self.simulation) for agent in self.agents.values()]

    # -----------------------------------------------------------------------
    # Task Assignment & Validation
    # -----------------------------------------------------------------------

    def validate_task_compatibility(self, agent_id: str, task_type: str) -> bool:
        """Verify that agent possesses capabilities required for the task."""
        allowed_types = self.CAPABILITIES.get(agent_id.upper(), [])
        return task_type.upper() in [t.upper() for t in allowed_types]

    def assign_task(self, agent_id: str, task: AgentTask) -> bool:
        """Assign task to agent, verifying capabilities and availability."""
        agent = self.get_agent(agent_id)
        if agent is None:
            raise ValueError(f"Agent '{agent_id}' is not registered.")

        # Check compatibility
        if not self.validate_task_compatibility(agent_id, task.task_type):
            raise ValueError(
                f"Incompatible task assignment: Agent '{agent_id}' ({agent.role}) cannot perform '{task.task_type}'. "
                f"Allowed task types: {self.CAPABILITIES.get(agent_id.upper())}."
            )

        # Check availability
        if agent.status not in ["IDLE", "COMPLETED"]:
            raise ValueError(f"Cannot assign task to '{agent_id}': Agent is currently {agent.status}.")

        task.assigned_agent_id = agent_id
        task.status = "IN_PROGRESS"
        agent.status = "ASSIGNED"
        agent.assigned_task = task.to_dict()
        agent.execution_result = None

        self.tasks[task.task_id] = task
        logger.info("Assigned task %s (%s) to agent %s.", task.task_id, task.task_type, agent_id)
        return True

    def execute_assigned_task(self, agent_id: str) -> Dict[str, Any]:
        """Execute assigned task using agent's deterministic behavior."""
        agent = self.get_agent(agent_id)
        if agent is None or agent.assigned_task is None:
            raise ValueError(f"Agent '{agent_id}' has no assigned task to execute.")

        if self.simulation is None or not self.simulation._is_initialized:
            raise RuntimeError("Simulation must be initialized before executing agent tasks.")

        task_id = agent.assigned_task.get("id")
        task_obj = self.tasks.get(task_id)

        try:
            result = agent.execute_task(agent.assigned_task.get("payload", {}), self.simulation, self.navigator)
            if result.get("success", False):
                self.handle_task_success(agent_id, task_id, result)
            else:
                self.handle_task_failure(agent_id, task_id, result.get("error", "Unknown task execution error"))
            return result
        except Exception as exc:
            self.handle_task_failure(agent_id, task_id, str(exc))
            return {"success": False, "agent_id": agent_id, "error": str(exc)}

    def handle_task_success(self, agent_id: str, task_id: str, result: Dict[str, Any]) -> None:
        """Record successful task completion."""
        agent = self.get_agent(agent_id)
        if agent:
            agent.status = "COMPLETED"
            agent.current_action = "IDLE"
            agent.execution_result = result

        task = self.tasks.get(task_id)
        if task:
            task.status = "COMPLETED"
            task.result = result

        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)
        logger.info("Task %s completed successfully by agent %s.", task_id, agent_id)

    def handle_task_failure(self, agent_id: str, task_id: str, error_message: str) -> None:
        """Handle task failure, logging error and setting agent state."""
        agent = self.get_agent(agent_id)
        if agent:
            agent.status = "FAILED"
            agent.current_action = "HALTED"
            agent.execution_result = {"success": False, "error": error_message}

        task = self.tasks.get(task_id)
        if task:
            task.status = "FAILED"
            task.error_message = error_message

        if task_id not in self.failed_tasks:
            self.failed_tasks.append(task_id)
        logger.error("Task %s failed for agent %s: %s", task_id, agent_id, error_message)

    def update_agent_status(self, agent_id: str, new_status: str) -> None:
        """Manually override or update an agent's status."""
        agent = self.get_agent(agent_id)
        if agent is None:
            raise ValueError(f"Agent '{agent_id}' does not exist.")
        valid_statuses = {"IDLE", "ASSIGNED", "MOVING", "WORKING", "COMPLETED", "FAILED", "PAUSED"}
        if new_status.upper() not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {valid_statuses}")
        agent.status = new_status.upper()
        logger.info("Agent %s status updated to %s.", agent_id, new_status.upper())


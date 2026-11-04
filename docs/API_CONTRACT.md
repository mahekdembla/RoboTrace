# RoboTrace 3D — API Contract

> **Version:** 1.0.0  
> **Base URL:** `http://localhost:8000`  
> **Protocol:** REST (JSON) + WebSocket  
> **Coordinate System:** Z-up, yaw rotation in radians

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. Domain Definitions](#2-domain-definitions)
  - [2.1 Agents](#21-agents)
  - [2.2 Mission Statuses](#22-mission-statuses)
  - [2.3 Agent Statuses](#23-agent-statuses)
  - [2.4 Error Categories](#24-error-categories)
  - [2.5 Review Statuses](#25-review-statuses)
  - [2.6 Coordinate System](#26-coordinate-system)
- [3. Common Conventions](#3-common-conventions)
- [4. Shared Schemas](#4-shared-schemas)
- [5. REST Endpoints](#5-rest-endpoints)
  - [5.1 Health Check](#51-health-check)
  - [5.2 Agents](#52-agents)
  - [5.3 Missions](#53-missions)
  - [5.4 Mission Lifecycle](#54-mission-lifecycle)
  - [5.5 Trajectory](#55-trajectory)
  - [5.6 Errors](#56-errors)
  - [5.7 Annotations](#57-annotations)
  - [5.8 Analytics](#58-analytics)
- [6. WebSocket](#6-websocket)
- [7. Error Responses](#7-error-responses)

---

## 1. Overview

RoboTrace 3D is a robotics simulation and tracing platform. The API enables:

- **Mission management** — create, start, pause, resume, and reset robotic missions.
- **Agent monitoring** — observe the state and position of each robotic agent.
- **Trajectory tracking** — replay the full observation → decision → action → outcome chain.
- **Error analysis** — review AI-predicted error categories (AgentGuard) and submit human corrections.
- **Real-time updates** — receive live simulation state via WebSocket.
- **Analytics** — aggregate performance metrics across missions and agents.

---

## 2. Domain Definitions

### 2.1 Agents

Three robotic agents operate within the simulation environment:

| Agent ID | Name    | Role                        | Description                                      |
|----------|---------|-----------------------------|--------------------------------------------------|
| `ATLAS`  | Atlas   | Package Pickup & Delivery   | Picks up packages from origin and delivers them to designated drop-off zones. |
| `NOVA`   | Nova    | Inventory Inspection        | Inspects inventory shelves, scans barcodes, and reports stock levels. |
| `TITAN`  | Titan   | Material Transportation     | Transports heavy materials between staging areas and work stations. |

### 2.2 Mission Statuses

| Status      | Description                                                    |
|-------------|----------------------------------------------------------------|
| `PENDING`   | Mission created but not yet started.                           |
| `RUNNING`   | Mission is actively executing.                                 |
| `PAUSED`    | Mission execution is temporarily suspended.                    |
| `COMPLETED` | Mission finished successfully.                                 |
| `FAILED`    | Mission terminated due to an unrecoverable error.              |

**Allowed state transitions:**

```
PENDING → RUNNING → PAUSED → RUNNING   (resume)
                   → COMPLETED
                   → FAILED
RUNNING → COMPLETED
RUNNING → FAILED
PAUSED  → RUNNING   (resume)
Any     → PENDING   (reset)
```

### 2.3 Agent Statuses

| Status      | Description                                                    |
|-------------|----------------------------------------------------------------|
| `IDLE`      | Agent is powered on but not assigned to any task.              |
| `ASSIGNED`  | Agent has been assigned a task but has not started moving.      |
| `MOVING`    | Agent is in transit toward a target position.                  |
| `WORKING`   | Agent is performing its primary operation (e.g. picking, scanning). |
| `COMPLETED` | Agent has finished its current task successfully.              |
| `FAILED`    | Agent encountered an error and cannot continue.                |
| `PAUSED`    | Agent execution is temporarily suspended.                      |

### 2.4 Error Categories

These categories are used by AgentGuard for automatic classification and by human reviewers for manual correction.

| Category          | Description                                                     |
|-------------------|-----------------------------------------------------------------|
| `PERCEPTION`      | Sensor failure, misread data, or object recognition error.      |
| `NAVIGATION`      | Path planning failure, route deviation, or localization error.  |
| `PLANNING`        | Task planning error, invalid goal state, or priority conflict.  |
| `MANIPULATION`    | Grasping failure, drop, or mechanical actuation error.          |
| `COLLISION`       | Contact with obstacle, wall, other agent, or environment.       |
| `EXECUTION`       | Action execution failure not covered by other categories.       |
| `RECOVERY`        | Failure during error-recovery procedures.                       |
| `TASK_COMPLETION` | Task reported complete but acceptance criteria not met.         |
| `COORDINATION`    | Multi-agent coordination or communication failure.              |

### 2.5 Review Statuses

Used on annotations to track the human review lifecycle:

| Status           | Description                                                      |
|------------------|------------------------------------------------------------------|
| `PENDING_REVIEW` | Error logged by AgentGuard; awaiting human review.               |
| `CONFIRMED`      | Human reviewer agrees with AgentGuard's suggested category.      |
| `REJECTED`       | Human reviewer disagrees; no correction provided yet.            |
| `CORRECTED`      | Human reviewer has supplied a corrected category.                |

### 2.6 Coordinate System

All position data uses a **right-handed, Z-up** coordinate system:

| Axis  | Direction       |
|-------|-----------------|
| **X** | Forward / East  |
| **Y** | Left / North    |
| **Z** | Up              |

- **Position** is expressed as `{ "x": float, "y": float, "z": float }` in metres.
- **Orientation** is expressed as `"yaw": float` in **radians** (rotation about the Z-axis).
  - `0` = facing +X
  - `π/2` = facing +Y
  - Range: `[-π, π]`
- **Velocity** is expressed as `"linear_velocity": float` (m/s) and `"angular_velocity": float` (rad/s).

---

## 3. Common Conventions

| Convention            | Rule                                                              |
|-----------------------|-------------------------------------------------------------------|
| **Content-Type**      | `application/json` for all request and response bodies.           |
| **Timestamps**        | ISO 8601 with timezone: `"2025-01-15T09:30:00Z"` (always UTC).   |
| **IDs**               | Integer auto-incremented primary keys.                            |
| **Enums**             | UPPER_SNAKE_CASE strings.                                         |
| **Pagination**        | Query params `?skip=0&limit=50` (defaults: skip=0, limit=50).    |
| **Nullability**       | Missing optional fields are `null` in responses, omitted in requests. |
| **Error format**      | `{ "detail": "..." }` for 4xx/5xx responses.                     |
| **Floating-point**    | Coordinates, scores, and velocities are IEEE 754 double-precision. |

---

## 4. Shared Schemas

### 4.1 Position

```json
{
  "x": 3.45,
  "y": -1.20,
  "z": 0.0
}
```

| Field | Type  | Required | Description              |
|-------|-------|----------|--------------------------|
| `x`   | float | ✅       | X coordinate (metres)    |
| `y`   | float | ✅       | Y coordinate (metres)    |
| `z`   | float | ✅       | Z coordinate (metres)    |

### 4.2 Pose (Position + Orientation)

```json
{
  "x": 3.45,
  "y": -1.20,
  "z": 0.0,
  "yaw": 1.5708
}
```

| Field | Type  | Required | Description                          |
|-------|-------|----------|--------------------------------------|
| `x`   | float | ✅       | X coordinate (metres)                |
| `y`   | float | ✅       | Y coordinate (metres)                |
| `z`   | float | ✅       | Z coordinate (metres)                |
| `yaw` | float | ✅       | Rotation about Z-axis (radians)      |

### 4.3 AgentSummary

```json
{
  "agent_id": "ATLAS",
  "name": "Atlas",
  "role": "Package Pickup & Delivery",
  "status": "MOVING",
  "current_pose": {
    "x": 3.45,
    "y": -1.20,
    "z": 0.0,
    "yaw": 1.5708
  },
  "linear_velocity": 0.8,
  "angular_velocity": 0.0,
  "current_task": "Deliver package to Zone B",
  "battery_level": 87.5
}
```

### 4.4 Timestamp Format

All timestamps are UTC, ISO 8601:

```
"2025-01-15T09:30:00Z"
```

---

## 5. REST Endpoints

---

### 5.1 Health Check

#### `GET /health`

Returns the current health status of the API server.

**Response `200 OK`**

```json
{
  "status": "healthy",
  "app": "RoboTrace3D",
  "version": "1.0.0",
  "timestamp": "2025-01-15T09:30:00Z"
}
```

| Field       | Type   | Description                 |
|-------------|--------|-----------------------------|
| `status`    | string | `"healthy"` or `"degraded"` |
| `app`       | string | Application name            |
| `version`   | string | API version                 |
| `timestamp` | string | Current server time (UTC)   |

---

### 5.2 Agents

#### `GET /api/agents`

Returns the list of all registered agents and their current states.

**Query Parameters**

| Param    | Type   | Default | Description                                    |
|----------|--------|---------|------------------------------------------------|
| `status` | string | —       | Filter by agent status (e.g. `MOVING`)         |

**Response `200 OK`**

```json
{
  "agents": [
    {
      "agent_id": "ATLAS",
      "name": "Atlas",
      "role": "Package Pickup & Delivery",
      "status": "MOVING",
      "current_pose": {
        "x": 3.45,
        "y": -1.20,
        "z": 0.0,
        "yaw": 1.5708
      },
      "linear_velocity": 0.8,
      "angular_velocity": 0.0,
      "current_task": "Deliver package to Zone B",
      "battery_level": 87.5
    },
    {
      "agent_id": "NOVA",
      "name": "Nova",
      "role": "Inventory Inspection",
      "status": "WORKING",
      "current_pose": {
        "x": 10.00,
        "y": 5.60,
        "z": 0.0,
        "yaw": 0.0
      },
      "linear_velocity": 0.0,
      "angular_velocity": 0.0,
      "current_task": "Scanning shelf row 3",
      "battery_level": 92.1
    },
    {
      "agent_id": "TITAN",
      "name": "Titan",
      "role": "Material Transportation",
      "status": "IDLE",
      "current_pose": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "yaw": 0.0
      },
      "linear_velocity": 0.0,
      "angular_velocity": 0.0,
      "current_task": null,
      "battery_level": 100.0
    }
  ]
}
```

---

### 5.3 Missions

#### `GET /api/missions`

Returns a paginated list of all missions.

**Query Parameters**

| Param    | Type   | Default | Description                                   |
|----------|--------|---------|-----------------------------------------------|
| `skip`   | int    | `0`     | Number of records to skip.                    |
| `limit`  | int    | `50`    | Maximum number of records to return.          |
| `status` | string | —       | Filter by mission status (e.g. `RUNNING`).    |

**Response `200 OK`**

```json
{
  "missions": [
    {
      "id": 1,
      "name": "Warehouse Alpha Run",
      "description": "Full warehouse cycle: pickup, inspect, transport.",
      "status": "COMPLETED",
      "environment": "warehouse_floor_1",
      "agents": ["ATLAS", "NOVA", "TITAN"],
      "created_at": "2025-01-15T08:00:00Z",
      "started_at": "2025-01-15T08:05:00Z",
      "ended_at": "2025-01-15T09:30:00Z",
      "duration_seconds": 5100
    },
    {
      "id": 2,
      "name": "Inspection Beta",
      "description": "Nova-only shelf inspection.",
      "status": "PENDING",
      "environment": "warehouse_floor_2",
      "agents": ["NOVA"],
      "created_at": "2025-01-15T10:00:00Z",
      "started_at": null,
      "ended_at": null,
      "duration_seconds": null
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 50
}
```

---

#### `POST /api/missions`

Creates a new mission in `PENDING` status.

**Request Body**

```json
{
  "name": "Warehouse Gamma Cycle",
  "description": "Atlas delivers, Nova inspects, Titan transports materials.",
  "environment": "warehouse_floor_1",
  "agents": ["ATLAS", "NOVA", "TITAN"]
}
```

| Field         | Type     | Required | Description                                |
|---------------|----------|----------|--------------------------------------------|
| `name`        | string   | ✅       | Mission name.                              |
| `description` | string   | ❌       | Optional description.                      |
| `environment` | string   | ❌       | Simulation environment ID.                 |
| `agents`      | string[] | ✅       | List of agent IDs to assign. Must be valid agent IDs (`ATLAS`, `NOVA`, `TITAN`). |

**Response `201 Created`**

```json
{
  "id": 3,
  "name": "Warehouse Gamma Cycle",
  "description": "Atlas delivers, Nova inspects, Titan transports materials.",
  "status": "PENDING",
  "environment": "warehouse_floor_1",
  "agents": ["ATLAS", "NOVA", "TITAN"],
  "created_at": "2025-01-15T12:00:00Z",
  "started_at": null,
  "ended_at": null,
  "duration_seconds": null
}
```

**Error `422 Unprocessable Entity`**

```json
{
  "detail": "Invalid agent ID: 'UNKNOWN'. Valid IDs: ATLAS, NOVA, TITAN."
}
```

---

#### `GET /api/missions/{mission_id}`

Returns full details for a single mission, including per-agent states and task progress.

**Path Parameters**

| Param        | Type | Description |
|--------------|------|-------------|
| `mission_id` | int  | Mission ID. |

**Response `200 OK`**

```json
{
  "id": 1,
  "name": "Warehouse Alpha Run",
  "description": "Full warehouse cycle: pickup, inspect, transport.",
  "status": "RUNNING",
  "environment": "warehouse_floor_1",
  "created_at": "2025-01-15T08:00:00Z",
  "started_at": "2025-01-15T08:05:00Z",
  "ended_at": null,
  "duration_seconds": 342,
  "agents": [
    {
      "agent_id": "ATLAS",
      "name": "Atlas",
      "status": "MOVING",
      "current_pose": {
        "x": 3.45,
        "y": -1.20,
        "z": 0.0,
        "yaw": 1.5708
      },
      "linear_velocity": 0.8,
      "angular_velocity": 0.0,
      "current_task": "Deliver package to Zone B"
    },
    {
      "agent_id": "NOVA",
      "name": "Nova",
      "status": "WORKING",
      "current_pose": {
        "x": 10.00,
        "y": 5.60,
        "z": 0.0,
        "yaw": 0.0
      },
      "linear_velocity": 0.0,
      "angular_velocity": 0.0,
      "current_task": "Scanning shelf row 3"
    },
    {
      "agent_id": "TITAN",
      "name": "Titan",
      "status": "ASSIGNED",
      "current_pose": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "yaw": 0.0
      },
      "linear_velocity": 0.0,
      "angular_velocity": 0.0,
      "current_task": "Transport steel beams to Station C"
    }
  ],
  "task_summary": {
    "total": 6,
    "completed": 2,
    "in_progress": 3,
    "pending": 1,
    "failed": 0
  },
  "error_count": 1
}
```

**Error `404 Not Found`**

```json
{
  "detail": "Mission with id 99 not found."
}
```

---

### 5.4 Mission Lifecycle

All lifecycle endpoints return the updated mission object.

---

#### `POST /api/missions/{mission_id}/start`

Transitions a mission from `PENDING` → `RUNNING`. Assigns tasks to agents and begins the simulation.

**Request Body:** None.

**Response `200 OK`**

```json
{
  "id": 3,
  "name": "Warehouse Gamma Cycle",
  "status": "RUNNING",
  "started_at": "2025-01-15T12:05:00Z",
  "message": "Mission started. 3 agents deployed."
}
```

**Error `409 Conflict`**

```json
{
  "detail": "Cannot start mission 3: current status is RUNNING. Only PENDING missions can be started."
}
```

---

#### `POST /api/missions/{mission_id}/pause`

Transitions a mission from `RUNNING` → `PAUSED`. All agents are paused in place.

**Request Body:** None.

**Response `200 OK`**

```json
{
  "id": 3,
  "name": "Warehouse Gamma Cycle",
  "status": "PAUSED",
  "message": "Mission paused. 3 agents halted."
}
```

**Error `409 Conflict`**

```json
{
  "detail": "Cannot pause mission 3: current status is PENDING. Only RUNNING missions can be paused."
}
```

---

#### `POST /api/missions/{mission_id}/resume`

Transitions a mission from `PAUSED` → `RUNNING`. All agents resume from their paused positions.

**Request Body:** None.

**Response `200 OK`**

```json
{
  "id": 3,
  "name": "Warehouse Gamma Cycle",
  "status": "RUNNING",
  "message": "Mission resumed. 3 agents reactivated."
}
```

**Error `409 Conflict`**

```json
{
  "detail": "Cannot resume mission 3: current status is RUNNING. Only PAUSED missions can be resumed."
}
```

---

#### `POST /api/missions/{mission_id}/reset`

Resets a mission back to `PENDING`. Clears all trajectory data, errors, and agent states. Agents return to initial positions.

**Request Body:** None.

**Response `200 OK`**

```json
{
  "id": 3,
  "name": "Warehouse Gamma Cycle",
  "status": "PENDING",
  "started_at": null,
  "ended_at": null,
  "message": "Mission reset. All trajectory data and errors cleared."
}
```

**Error `404 Not Found`**

```json
{
  "detail": "Mission with id 99 not found."
}
```

---

### 5.5 Trajectory

#### `GET /api/missions/{mission_id}/trajectory`

Returns the full trajectory event log for a mission — the time-ordered sequence of position snapshots, observations, decisions, actions, and outcomes.

**Path Parameters**

| Param        | Type | Description |
|--------------|------|-------------|
| `mission_id` | int  | Mission ID. |

**Query Parameters**

| Param      | Type   | Default | Description                                    |
|------------|--------|---------|------------------------------------------------|
| `agent_id` | string | —       | Filter by agent (e.g. `ATLAS`).                |
| `skip`     | int    | `0`     | Number of events to skip.                      |
| `limit`    | int    | `200`   | Maximum events to return.                      |

**Response `200 OK`**

```json
{
  "mission_id": 1,
  "events": [
    {
      "id": 1,
      "agent_id": "ATLAS",
      "timestamp": "2025-01-15T08:05:01Z",
      "pose": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "yaw": 0.0
      },
      "linear_velocity": 0.0,
      "angular_velocity": 0.0,
      "observation": "Package detected at origin point. Barcode scanned: PKG-1042.",
      "decision_summary": "Navigate to package pickup zone. Shortest path via aisle 2.",
      "action": "MOVE_TO(2.5, 0.0, 0.0)",
      "outcome": "Movement initiated. ETA 4.2 seconds."
    },
    {
      "id": 2,
      "agent_id": "ATLAS",
      "timestamp": "2025-01-15T08:05:05Z",
      "pose": {
        "x": 2.50,
        "y": 0.0,
        "z": 0.0,
        "yaw": 0.0
      },
      "linear_velocity": 0.6,
      "angular_velocity": 0.0,
      "observation": "Arrived at pickup zone. Package PKG-1042 within grasp range.",
      "decision_summary": "Initiate package pickup. Gripper alignment confirmed.",
      "action": "PICK_UP(PKG-1042)",
      "outcome": "Package secured. Grip force nominal."
    },
    {
      "id": 3,
      "agent_id": "ATLAS",
      "timestamp": "2025-01-15T08:05:06Z",
      "pose": {
        "x": 2.50,
        "y": 0.0,
        "z": 0.0,
        "yaw": 3.1416
      },
      "linear_velocity": 0.0,
      "angular_velocity": 1.2,
      "observation": "Package held. Delivery zone B located at (8.0, 3.0, 0.0).",
      "decision_summary": "Rotate 180° and navigate to delivery zone B via aisle 3.",
      "action": "ROTATE(3.1416) → MOVE_TO(8.0, 3.0, 0.0)",
      "outcome": "Rotation complete. Beginning transit to Zone B."
    },
    {
      "id": 10,
      "agent_id": "NOVA",
      "timestamp": "2025-01-15T08:05:02Z",
      "pose": {
        "x": 10.00,
        "y": 4.20,
        "z": 0.0,
        "yaw": 1.5708
      },
      "linear_velocity": 0.3,
      "angular_velocity": 0.0,
      "observation": "Approaching shelf row 3. 12 items expected per manifest.",
      "decision_summary": "Begin sequential barcode scan from position S3-A to S3-L.",
      "action": "SCAN_SHELF(row=3, start=A, end=L)",
      "outcome": "Scan initiated. 3 of 12 items scanned so far."
    }
  ],
  "total": 156,
  "skip": 0,
  "limit": 200
}
```

---

### 5.6 Errors

#### `GET /api/errors`

Returns errors across all missions. Each error includes the **original AgentGuard prediction** (`suggested_category`) and its current review status.

**Query Parameters**

| Param        | Type   | Default | Description                                          |
|--------------|--------|---------|------------------------------------------------------|
| `mission_id` | int    | —       | Filter by mission.                                   |
| `agent_id`   | string | —       | Filter by agent (e.g. `TITAN`).                      |
| `severity`   | string | —       | Filter by severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`). |
| `category`   | string | —       | Filter by suggested category (e.g. `COLLISION`).     |
| `is_resolved`| bool   | —       | Filter by resolution status.                         |
| `skip`       | int    | `0`     | Number of records to skip.                           |
| `limit`      | int    | `50`    | Maximum records to return.                           |

**Response `200 OK`**

```json
{
  "errors": [
    {
      "id": 1,
      "mission_id": 1,
      "task_id": 3,
      "agent_id": "ATLAS",
      "timestamp": "2025-01-15T08:12:45Z",
      "error_code": "NAV-001",
      "error_message": "Path blocked by unexpected obstacle at (5.2, 1.8, 0.0). Replanning failed after 3 attempts.",
      "severity": "HIGH",
      "suggested_category": "NAVIGATION",
      "is_resolved": false,
      "resolved_at": null,
      "resolution_notes": null,
      "review_status": "PENDING_REVIEW",
      "created_at": "2025-01-15T08:12:45Z"
    },
    {
      "id": 2,
      "mission_id": 1,
      "task_id": 5,
      "agent_id": "TITAN",
      "timestamp": "2025-01-15T08:20:10Z",
      "error_code": "MAN-003",
      "error_message": "Gripper slippage detected during material lift. Load exceeded safe threshold by 12%.",
      "severity": "CRITICAL",
      "suggested_category": "MANIPULATION",
      "is_resolved": true,
      "resolved_at": "2025-01-15T08:22:30Z",
      "resolution_notes": "Grip recalibrated. Load redistributed to secondary mount.",
      "review_status": "CORRECTED",
      "created_at": "2025-01-15T08:20:10Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 50
}
```

---

### 5.7 Annotations

#### `GET /api/annotations`

Returns all human annotations. Each annotation references an error and stores the **corrected category** separately from the original AgentGuard prediction.

**Query Parameters**

| Param           | Type   | Default | Description                                      |
|-----------------|--------|---------|--------------------------------------------------|
| `error_id`      | int    | —       | Filter by error.                                 |
| `review_status` | string | —       | Filter by review status (e.g. `CORRECTED`).      |
| `annotator`     | string | —       | Filter by annotator.                             |
| `skip`          | int    | `0`     | Number of records to skip.                       |
| `limit`         | int    | `50`    | Maximum records to return.                       |

**Response `200 OK`**

```json
{
  "annotations": [
    {
      "id": 1,
      "error_id": 2,
      "original_suggested_category": "MANIPULATION",
      "corrected_category": "PERCEPTION",
      "review_status": "CORRECTED",
      "annotator": "dr.chen@robotrace.dev",
      "notes": "Root cause was a faulty weight sensor reading, not a mechanical gripper issue. The load was within safe limits but the sensor reported an inflated value.",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

> **Note:** `original_suggested_category` is read from the parent `Error.suggested_category` and is **never modified** by annotation submission.

---

#### `POST /api/annotations`

Submits a human annotation for an error. This creates a new annotation record — it **never overwrites** the original `Error.suggested_category`.

**Request Body**

```json
{
  "error_id": 1,
  "corrected_category": "COLLISION",
  "review_status": "CORRECTED",
  "annotator": "dr.chen@robotrace.dev",
  "notes": "The obstacle was another agent (TITAN) that entered Atlas's planned path. This is a coordination issue manifesting as a navigation failure, but the root cause is collision avoidance."
}
```

| Field                | Type   | Required | Description                                            |
|----------------------|--------|----------|--------------------------------------------------------|
| `error_id`           | int    | ✅       | ID of the error being annotated.                       |
| `corrected_category` | string | ✅       | Human-corrected category. Must be a valid error category. |
| `review_status`      | string | ✅       | One of: `CONFIRMED`, `REJECTED`, `CORRECTED`.          |
| `annotator`          | string | ✅       | Identifier for the human reviewer.                     |
| `notes`              | string | ❌       | Explanation for the correction.                        |

**Validation rules:**
- `error_id` must reference an existing error.
- `corrected_category` must be one of the nine valid error categories.
- `review_status` must be `CONFIRMED`, `REJECTED`, or `CORRECTED`. (`PENDING_REVIEW` is system-assigned only.)
- If `review_status` is `CONFIRMED`, `corrected_category` should match the original `suggested_category`.
- If `review_status` is `CORRECTED`, `corrected_category` should differ from `suggested_category`.

**Response `201 Created`**

```json
{
  "id": 2,
  "error_id": 1,
  "original_suggested_category": "NAVIGATION",
  "corrected_category": "COLLISION",
  "review_status": "CORRECTED",
  "annotator": "dr.chen@robotrace.dev",
  "notes": "The obstacle was another agent (TITAN) that entered Atlas's planned path. This is a coordination issue manifesting as a navigation failure, but the root cause is collision avoidance.",
  "created_at": "2025-01-15T11:30:00Z",
  "updated_at": "2025-01-15T11:30:00Z"
}
```

**Error `422 Unprocessable Entity`**

```json
{
  "detail": "Invalid corrected_category: 'UNKNOWN'. Valid categories: PERCEPTION, NAVIGATION, PLANNING, MANIPULATION, COLLISION, EXECUTION, RECOVERY, TASK_COMPLETION, COORDINATION."
}
```

**Error `404 Not Found`**

```json
{
  "detail": "Error with id 99 not found."
}
```

---

### 5.8 Analytics

#### `GET /api/analytics`

Returns aggregated performance metrics across missions and agents.

**Query Parameters**

| Param        | Type   | Default | Description                              |
|--------------|--------|---------|------------------------------------------|
| `mission_id` | int    | —       | Scope to a specific mission.             |
| `agent_id`   | string | —       | Scope to a specific agent.               |

**Response `200 OK`**

```json
{
  "summary": {
    "total_missions": 12,
    "missions_completed": 9,
    "missions_failed": 2,
    "missions_pending": 1,
    "overall_success_rate": 0.75
  },
  "agent_performance": [
    {
      "agent_id": "ATLAS",
      "name": "Atlas",
      "missions_participated": 10,
      "tasks_completed": 42,
      "tasks_failed": 3,
      "total_distance_m": 1284.5,
      "total_errors": 5,
      "avg_task_duration_seconds": 185.3,
      "success_rate": 0.93
    },
    {
      "agent_id": "NOVA",
      "name": "Nova",
      "missions_participated": 8,
      "tasks_completed": 64,
      "tasks_failed": 1,
      "total_distance_m": 642.0,
      "total_errors": 2,
      "avg_task_duration_seconds": 92.7,
      "success_rate": 0.98
    },
    {
      "agent_id": "TITAN",
      "name": "Titan",
      "missions_participated": 7,
      "tasks_completed": 28,
      "tasks_failed": 4,
      "total_distance_m": 2105.8,
      "total_errors": 8,
      "avg_task_duration_seconds": 310.6,
      "success_rate": 0.88
    }
  ],
  "error_breakdown": {
    "by_category": {
      "NAVIGATION": 4,
      "MANIPULATION": 3,
      "COLLISION": 3,
      "PERCEPTION": 2,
      "PLANNING": 1,
      "EXECUTION": 1,
      "COORDINATION": 1,
      "RECOVERY": 0,
      "TASK_COMPLETION": 0
    },
    "by_severity": {
      "CRITICAL": 2,
      "HIGH": 5,
      "MEDIUM": 6,
      "LOW": 2
    },
    "total_errors": 15,
    "resolved_count": 12,
    "unresolved_count": 3
  },
  "annotation_stats": {
    "total_annotations": 10,
    "confirmed": 6,
    "corrected": 3,
    "rejected": 1,
    "pending_review": 5,
    "agentguard_accuracy": 0.60
  }
}
```

| Field                              | Description                                               |
|------------------------------------|-----------------------------------------------------------|
| `summary.overall_success_rate`     | `missions_completed / (completed + failed)`               |
| `agent_performance[].success_rate` | `tasks_completed / (completed + failed)` per agent        |
| `annotation_stats.agentguard_accuracy` | Fraction of annotations where the human **confirmed** the original prediction. |

---

## 6. WebSocket

### `WS /ws/simulation`

Provides real-time simulation state updates. The client connects once and receives a continuous stream of JSON messages.

**Connection URL**

```
ws://localhost:8000/ws/simulation
```

**Query Parameters (on connect)**

| Param        | Type | Default | Description                                  |
|--------------|------|---------|----------------------------------------------|
| `mission_id` | int  | —       | Subscribe to a specific mission's updates.   |

**Example:** `ws://localhost:8000/ws/simulation?mission_id=3`

---

### 6.1 Server → Client Messages

All server messages follow this envelope:

```json
{
  "type": "<message_type>",
  "timestamp": "2025-01-15T08:05:01Z",
  "data": { ... }
}
```

---

#### `AGENT_STATE` — Agent position/status update

Sent at each simulation tick (typically 10 Hz).

```json
{
  "type": "AGENT_STATE",
  "timestamp": "2025-01-15T08:05:01Z",
  "data": {
    "mission_id": 3,
    "agent_id": "ATLAS",
    "status": "MOVING",
    "pose": {
      "x": 3.45,
      "y": -1.20,
      "z": 0.0,
      "yaw": 1.5708
    },
    "linear_velocity": 0.8,
    "angular_velocity": 0.0,
    "current_task": "Deliver package to Zone B"
  }
}
```

---

#### `TRAJECTORY_EVENT` — Observation/Decision/Action/Outcome logged

Sent when a significant trajectory event is recorded.

```json
{
  "type": "TRAJECTORY_EVENT",
  "timestamp": "2025-01-15T08:05:05Z",
  "data": {
    "mission_id": 3,
    "event_id": 42,
    "agent_id": "ATLAS",
    "pose": {
      "x": 2.50,
      "y": 0.0,
      "z": 0.0,
      "yaw": 0.0
    },
    "observation": "Arrived at pickup zone. Package PKG-1042 within grasp range.",
    "decision_summary": "Initiate package pickup. Gripper alignment confirmed.",
    "action": "PICK_UP(PKG-1042)",
    "outcome": "Package secured. Grip force nominal."
  }
}
```

---

#### `MISSION_STATUS` — Mission state transition

Sent when the mission status changes.

```json
{
  "type": "MISSION_STATUS",
  "timestamp": "2025-01-15T08:05:00Z",
  "data": {
    "mission_id": 3,
    "previous_status": "PENDING",
    "new_status": "RUNNING",
    "message": "Mission started. 3 agents deployed."
  }
}
```

---

#### `ERROR_OCCURRED` — New error detected

Sent when AgentGuard logs a new error.

```json
{
  "type": "ERROR_OCCURRED",
  "timestamp": "2025-01-15T08:12:45Z",
  "data": {
    "mission_id": 3,
    "error_id": 7,
    "agent_id": "ATLAS",
    "error_code": "NAV-001",
    "error_message": "Path blocked by unexpected obstacle at (5.2, 1.8, 0.0).",
    "severity": "HIGH",
    "suggested_category": "NAVIGATION",
    "review_status": "PENDING_REVIEW"
  }
}
```

---

#### `TASK_UPDATE` — Task progress change

Sent when a task's status changes.

```json
{
  "type": "TASK_UPDATE",
  "timestamp": "2025-01-15T08:15:00Z",
  "data": {
    "mission_id": 3,
    "task_id": 5,
    "agent_id": "NOVA",
    "task_name": "Scan shelf row 3",
    "previous_status": "IN_PROGRESS",
    "new_status": "COMPLETED"
  }
}
```

---

#### `ANNOTATION_SUBMITTED` — Human review completed

Sent when a new annotation is submitted via `POST /api/annotations`.

```json
{
  "type": "ANNOTATION_SUBMITTED",
  "timestamp": "2025-01-15T11:30:00Z",
  "data": {
    "annotation_id": 2,
    "error_id": 1,
    "original_suggested_category": "NAVIGATION",
    "corrected_category": "COLLISION",
    "review_status": "CORRECTED",
    "annotator": "dr.chen@robotrace.dev"
  }
}
```

---

### 6.2 Client → Server Messages

#### `PING` — Keep-alive

```json
{
  "type": "PING"
}
```

**Server replies:**

```json
{
  "type": "PONG",
  "timestamp": "2025-01-15T08:05:01Z"
}
```

---

#### `SUBSCRIBE` — Change subscription

Switch to a different mission without reconnecting.

```json
{
  "type": "SUBSCRIBE",
  "data": {
    "mission_id": 5
  }
}
```

**Server replies:**

```json
{
  "type": "SUBSCRIBED",
  "timestamp": "2025-01-15T08:05:01Z",
  "data": {
    "mission_id": 5,
    "message": "Now receiving updates for mission 5."
  }
}
```

---

## 7. Error Responses

All error responses follow the same structure:

```json
{
  "detail": "Human-readable error message."
}
```

### HTTP Status Codes

| Code  | Meaning                | When used                                              |
|-------|------------------------|--------------------------------------------------------|
| `200` | OK                     | Successful GET, successful lifecycle action.           |
| `201` | Created                | Successful POST that creates a resource.               |
| `400` | Bad Request            | Malformed JSON or invalid query parameter.             |
| `404` | Not Found              | Resource ID does not exist.                            |
| `409` | Conflict               | Invalid state transition (e.g. pausing a pending mission). |
| `422` | Unprocessable Entity   | Valid JSON but semantically invalid (bad enum, missing field). |
| `500` | Internal Server Error  | Unexpected server-side failure.                        |

### WebSocket Close Codes

| Code   | Meaning                  | When used                                   |
|--------|--------------------------|---------------------------------------------|
| `1000` | Normal Closure           | Client or server closes cleanly.            |
| `1003` | Unsupported Data         | Received non-JSON or unknown message type.  |
| `1008` | Policy Violation         | Invalid `mission_id` on connect.            |
| `1011` | Internal Error           | Unexpected server-side failure.             |

---

*End of API Contract v1.0.0*


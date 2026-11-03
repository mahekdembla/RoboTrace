# RoboTrace 3D
## Multi-Agent Robotic Simulation, Trajectory Intelligence & Decision Auditing Platform

**Project Type:** Robotics Simulation + AI Agent Evaluation + Human-in-the-Loop Annotation

**Development Approach:** Two-person collaborative development

**Target:** Functional one-day MVP, with scope for future enhancement

---

# 1. PROJECT OVERVIEW — WHAT ARE WE BUILDING?

RoboTrace 3D is a 3D robotics simulation and AI agent evaluation platform. It creates a virtual warehouse in which multiple autonomous robots perform different tasks, such as picking packages, transporting materials, and inspecting inventory.

However, the project is not just about showing robots moving inside a 3D environment. Its main purpose is to monitor and evaluate how these robots perform their tasks, record every action they take, identify incorrect decisions, locate the exact step where something goes wrong, and allow a human reviewer to verify and correct those errors.

Think of a company that uses AI-powered robots in its warehouse. The company wants to know whether its robots are completing tasks correctly. It also wants to understand why a robot failed, whether it selected the wrong route, whether it collided with an obstacle, or whether it incorrectly reported that a task was completed.

RoboTrace 3D provides a platform to investigate all of these situations.

The platform has two major modules:

**1. RoboTrace:** Responsible for the 3D robotic simulation, recording robot movements, storing action sequences, and replaying trajectories.

**2. AgentGuard:** Responsible for evaluating robot behaviour, detecting errors, classifying failures, and providing a human annotation interface.

The ultimate objective is to evaluate not only whether an agent completes a task, but also how it performs, where it fails, and how its decisions can be improved through human feedback.

---

# 2. UNDERSTANDING THE PROJECT THROUGH A REAL-LIFE SCENARIO

Imagine a large warehouse that receives hundreds of packages every day.

Instead of employing people to move every package, the warehouse uses three autonomous robots.

We will create three agents:

### Agent 1: Atlas — Pick & Delivery Agent

**Responsibility:** Pick a package from a shelf and deliver it to a specified station.

Simple explanation: Atlas is like a warehouse worker whose job is to collect packages and deliver them.

Technical explanation: Atlas receives a structured task containing the package ID, pickup location, destination, and expected result. It calculates a route, navigates towards the shelf, performs a grasp action, transports the package, and places it at the destination.

### Agent 2: Nova — Inventory Inspection Agent

**Responsibility:** Inspect warehouse shelves and identify missing or misplaced packages.

Simple explanation: Nova is like an inventory manager who checks whether all products are present and stored in the correct locations.

Technical explanation: Nova receives an inspection task, visits designated shelves, checks the simulated inventory state, compares the expected and actual package positions, and generates an inventory report.

### Agent 3: Titan — Material Transport Agent

**Responsibility:** Transport packages and materials between warehouse stations.

Simple explanation: Titan is like a delivery assistant who moves materials from one location to another.

Technical explanation: Titan receives a transport task, calculates a route between stations, checks for occupied paths, and executes its movement while considering the positions of other agents.

These are three different task-specific agent policies. They do not need to be three separate LLMs. For the first version, we will implement rule-based autonomous behaviour.

## Example warehouse mission

The warehouse manager gives the following instructions:

- Atlas: Pick package P-101 from Shelf A and deliver it to Station B.
- Nova: Inspect Shelves C and D and report misplaced packages.
- Titan: Transport package P-205 from Station X to Station Y.

All three agents receive their tasks and operate in the same virtual warehouse.

Now consider a situation where Atlas takes an incorrect route and collides with a shelf.

Atlas may fail to pick up the package, but it might still report that the delivery was successful.

RoboTrace records its complete sequence of actions, and AgentGuard checks what actually happened.

The system identifies that Atlas selected an invalid route, records the collision, and flags the incorrect task-completion claim.

A human reviewer can then inspect the failure, confirm the error category, and provide feedback.

This is the complete idea behind RoboTrace 3D.

---

# 3. COMPLETE SYSTEM WORKFLOW

The application will follow this sequence:

**Step 1 — Mission Creation**

The user creates a warehouse mission and defines tasks for the robots.

**Step 2 — Task Assignment**

The task scheduler assigns each task to the appropriate agent.

**Step 3 — Agent Execution**

Atlas, Nova, and Titan receive their tasks and decide which actions they need to perform.

**Step 4 — 3D Simulation**

The robots move around the warehouse, navigate routes, interact with packages, and complete their tasks.

**Step 5 — Trajectory Recording**

Every important action is recorded, including the robot's position, observation, decision summary, action, timestamp, and outcome.

**Step 6 — Decision Evaluation**

AgentGuard checks whether the actions were valid and whether the task was completed correctly.

**Step 7 — Error Detection**

If something goes wrong, the system identifies the failed step and classifies the error.

**Step 8 — Human Annotation**

A reviewer checks the detected error and accepts or corrects the suggested label.

**Step 9 — Analytics**

The system calculates performance metrics and compares the behaviour of different agents.

---

# 4. DIVISION OF WORK BETWEEN TWO TEAM MEMBERS

We will divide the project into two independent development parts.

The division is:

- **TEAM MEMBER 1 — Frontend, 3D Environment and User Interface**
- **TEAM MEMBER 2 — Python Backend, Robotics Simulation and Agent Evaluation**

Both members will work in the same GitHub repository but in separate folders.

## PART 1 — FRONTEND + 3D SIMULATION VISUALIZATION

**Responsible person: Team Member 1**

### What is the responsibility of this part?

This part is responsible for everything the user sees and interacts with.

It creates the application interface, displays the warehouse in 3D, shows the robots, provides mission controls, and displays information received from the Python backend.

In simple language, this person builds the actual application that the warehouse manager or human reviewer will use.

The frontend does not independently decide how the robots should behave. It receives their actual simulation state from the backend and displays it.

### A. Application structure and navigation

**Simple explanation:**

When a user opens RoboTrace 3D, they should see an organized dashboard with a sidebar. They can navigate between different sections without opening separate applications.

**Technical implementation:**

Use React Router to create six navigable pages inside one React application.

Pages:

1. Overview
2. 3D Simulation
3. Trajectories
4. AgentGuard
5. Annotations
6. Analytics

Create reusable components such as Sidebar, Header, AgentCard, MissionCard, and MetricCard.

### B. Overview dashboard

**Simple explanation:**

This is the control centre of the warehouse. The user can see how many robots are working, which tasks are running, which tasks are completed, and whether any robot has encountered an error.

**Technical implementation:**

Create a dashboard containing:

- Total number of agents
- Active agents
- Completed missions
- Failed missions
- Pending annotations
- Recent errors
- Agent status cards

The data should come from the backend API rather than being permanently hardcoded.

### C. 3D warehouse simulation interface

**Simple explanation:**

This is the main visual part of the project. The user should be able to see a virtual warehouse with shelves, packages, delivery stations, obstacles, and three robots.

When the robots execute their tasks, the user should see them moving around the warehouse.

**Technical implementation:**

Use:

- Three.js
- React Three Fiber
- Drei

Create a warehouse scene containing:

- Warehouse floor
- Shelves and racks
- Packages and boxes
- Pickup and delivery stations
- Obstacles
- Three robot models
- Camera controls
- Robot movement visualization
- Planned and actual trajectory lines

Use existing GLB/GLTF models where possible instead of creating complicated robot models from scratch.

The frontend receives robot coordinates and rotation values from the backend and updates the corresponding 3D models.

For example, if Atlas moves from position (2, 0, 3) to (4, 0, 5), its 3D representation should move accordingly.

**Important:** The Python simulation is the source of truth for robot positions. React should visualize those positions rather than independently calculating a conflicting movement path.

### D. Mission controls

**Simple explanation:**

The user needs buttons to control the simulation.

For example, the user should be able to start a mission, pause the robots, resume execution, and reset the environment.

**Technical implementation:**

Create controls for:

- Start mission
- Pause mission
- Resume mission
- Reset mission
- Select mission
- Select agent
- Playback speed

These controls should call the corresponding FastAPI endpoints.

### E. Trajectory visualization

**Simple explanation:**

Suppose Atlas moves through five different locations before delivering a package. The user should be able to see the route it followed and inspect each action.

If Atlas made a mistake at Step 3, the user should be able to select Step 3 and inspect what happened.

**Technical implementation:**

Create:

- Trajectory timeline
- Step-by-step event list
- Agent position history
- Planned route visualization
- Actual route visualization
- Playback and replay controls
- Selected-step information panel

The timeline data comes from the backend's trajectory recorder.

### F. AgentGuard interface

**Simple explanation:**

This page displays the mistakes detected by the evaluation system.

For example, it may show that Atlas collided with Shelf A or Nova incorrectly identified a package.

The user can inspect the problem and understand why it was flagged.

**Technical implementation:**

Create an error monitoring interface with:

- Error list
- Agent ID
- Failed step ID
- Error category
- Severity
- Evidence or event details
- Review status
- Link to the corresponding trajectory step

### G. Human annotation interface

**Simple explanation:**

The system may automatically suggest that an error occurred, but a human must verify whether the suggested error is correct.

The reviewer can accept the suggested category or change it.

For example, AgentGuard identifies an error as a navigation error. The reviewer inspects the trajectory and decides that the actual problem was a planning error.

**Technical implementation:**

Create an annotation form with:

- Suggested error category
- Final error category
- Severity
- Accept/reject decision
- Reviewer feedback
- Reviewed status

When the reviewer submits the annotation, the frontend sends the information to the Python backend.

### H. Analytics dashboard

**Simple explanation:**

This page helps the warehouse manager understand how well the robots performed.

For example, it can show how many missions were completed, how many errors occurred, and which agent performed better.

**Technical implementation:**

Use Recharts to create:

- Task success rate chart
- Error distribution chart
- Agent comparison chart
- Collision count
- Recovery rate
- Mission completion statistics

The metrics should be calculated by the backend.

### PART 1 — FINAL DELIVERABLES

The frontend developer must provide:

1. Complete React application.
2. Six working navigable pages.
3. 3D warehouse environment.
4. Three visible robot models.
5. Simulation controls.
6. Live robot visualization.
7. Trajectory timeline and replay interface.
8. AgentGuard error dashboard.
9. Human annotation interface.
10. Analytics dashboard.
11. API integration with the backend.

The main goal is to deliver a frontend that can display real simulation data and allow users to interact with the entire system.

---

## PART 2 — PYTHON BACKEND + ROBOTICS + AGENT EVALUATION

**Responsible person: Team Member 2**

### What is the responsibility of this part?

This part is responsible for the logic that operates behind the application.

It controls the agents, executes tasks, manages robot movements, records trajectories, detects errors, and stores the evaluation results.

In simple language, if Part 1 creates the screen that allows a person to watch the robots, Part 2 creates the system that makes the robots work and checks whether they are working correctly.

### A. FastAPI backend

**Simple explanation:**

The frontend and backend are two different parts of the application. They need a communication channel to exchange information.

FastAPI acts as a bridge between them.

For example, when the user clicks Start Mission, the frontend sends a request to FastAPI. FastAPI tells the Python system to start executing the mission.

**Technical implementation:**

Use Python and FastAPI to create REST API endpoints and WebSocket communication.

REST APIs will handle requests such as:

- Create mission
- Get agents
- Start mission
- Pause mission
- Get trajectories
- Get errors
- Submit annotations
- Get analytics

WebSockets will provide continuous updates for robot positions, agent status, and simulation events.

### B. Agent manager

**Simple explanation:**

The system needs to know which robots exist, what their responsibilities are, and which tasks they are currently performing.

The agent manager handles these responsibilities.

**Technical implementation:**

Create an agent registry to manage:

- Agent ID
- Agent name
- Agent type
- Current status
- Assigned task
- Current position
- Task execution state

Create three task-specific agents:

**Atlas:** Package pickup and delivery policy.

**Nova:** Inventory inspection policy.

**Titan:** Material transportation policy.

Initially, these agents can use rule-based logic rather than complex LLM-based reasoning.

### C. Task scheduler

**Simple explanation:**

Imagine that the warehouse receives three different tasks. The system needs to assign the correct task to the correct robot.

The task scheduler does that.

It also checks whether a task is ready to start and whether another robot is using a shared location.

**Technical implementation:**

Create a scheduler that:

- Receives mission tasks.
- Assigns tasks to agents.
- Tracks task status.
- Handles task priorities.
- Checks basic task dependencies.
- Coordinates access to shared warehouse areas.

For the MVP, simple task allocation and basic conflict prevention are sufficient.

### D. PyBullet simulation

**Simple explanation:**

The robots need an environment in which they can move and interact with objects.

PyBullet provides a physics-based simulation environment.

It allows the system to represent objects, robot movement, collisions, and basic physical interactions.

**Technical implementation:**

Use PyBullet to:

- Create the simulated warehouse environment.
- Load robot models using URDF where available.
- Set robot positions and orientations.
- Simulate movement.
- Detect collisions.
- Simulate package pickup and placement.
- Track object positions.

The PyBullet environment is the backend simulation. The React application will display the corresponding state in its 3D scene.

If full robot-arm manipulation becomes too time-consuming, implement a simplified grasp-and-place interaction for the first prototype.

### E. Navigation system

**Simple explanation:**

A robot needs to know how to reach its destination without hitting shelves or other robots.

The navigation module calculates a route and controls how the robot moves along it.

**Technical implementation:**

Implement:

- Start and destination coordinates.
- Basic path planning.
- Obstacle checks.
- Movement commands.
- Route validation.
- Simple collision avoidance.

A grid-based or waypoint-based navigation algorithm is sufficient for the initial implementation.

### F. RoboTrace — Trajectory recorder

**Simple explanation:**

Every action performed by a robot should be recorded.

For example, if Atlas performs ten actions during a delivery mission, RoboTrace should store those actions in the correct sequence.

If the robot fails, we should be able to look back at its complete sequence and identify where it went wrong.

**Technical implementation:**

Create a trajectory recorder that stores:

- Mission ID
- Agent ID
- Task ID
- Step ID
- Timestamp
- Observation
- Decision summary
- Action performed
- Expected outcome
- Actual outcome
- Execution status
- Robot coordinates

Each action should generate a structured event.

Example:

{
  "mission_id": "MISSION-001",
  "agent_id": "ATLAS",
  "step_id": 3,
  "observation": "Obstacle detected ahead",
  "decision_summary": "Robot attempts to move right",
  "action": "MOVE_RIGHT",
  "expected_outcome": "Avoid obstacle",
  "actual_outcome": "Collision detected",
  "status": "FAILED"
}

This data will be sent to the frontend so the user can view and replay the trajectory.

### G. AgentGuard — Decision evaluation

**Simple explanation:**

Recording a robot's movements is not enough. We also need to check whether its actions were correct.

AgentGuard acts like an independent quality inspector.

It checks the robot's actions and compares what should have happened with what actually happened.

**Technical implementation:**

Create rule-based evaluation logic that checks:

- Whether the robot selected a valid route.
- Whether an obstacle was avoided.
- Whether the pickup action was successful.
- Whether the package reached the correct destination.
- Whether an agent reported success incorrectly.
- Whether two agents attempted to occupy the same restricted space.
- Whether a robot repeated an action unnecessarily.

AgentGuard should inspect actual simulation events and task conditions instead of trusting an agent's own success report.

### H. Error classification

**Simple explanation:**

When a robot makes a mistake, we should identify what kind of mistake it made.

For example, hitting a shelf and picking the wrong package are two different problems.

**Technical implementation:**

Create an error taxonomy containing:

1. Perception Error — Robot failed to identify an object or obstacle.
2. Navigation Error — Robot selected an invalid route.
3. Planning Error — Robot selected an action that was not appropriate for the task.
4. Manipulation Error — Robot failed to pick or place a package.
5. Collision Error — Robot collided with an obstacle or another robot.
6. Execution Error — Robot performed an incorrect movement or action.
7. Recovery Error — Robot failed to recover after an error.
8. Task Completion Error — Robot reported completion without achieving the expected result.
9. Coordination Error — Multiple agents interfered with each other's tasks.

Each detected error should contain:

- Error ID
- Agent ID
- Failed step
- Error category
- Severity: Low, Medium or High
- Description
- Supporting evidence
- Review status

### I. Annotation manager

**Simple explanation:**

After AgentGuard identifies a possible error, a human reviewer checks it.

The annotation manager saves the reviewer's decision and feedback.

For example, the system suggests a collision error. The reviewer confirms it and adds a note explaining that the robot should have selected an alternative route.

**Technical implementation:**

Create functionality to:

- Receive human annotation submissions.
- Save the final error label.
- Store reviewer feedback.
- Track whether an annotation has been reviewed.
- Preserve the original suggested label.
- Store the corrected label separately.

Human feedback can later be used to improve agent policies or evaluation rules. Do not claim that every annotation automatically trains an AI model.

### J. Analytics and metrics

**Simple explanation:**

Once the robots finish their missions, the system should calculate how well they performed.

For example, we should know how many tasks Atlas completed successfully and how many errors Titan encountered.

**Technical implementation:**

Calculate:

- Task success rate.
- Total number of errors.
- Collision rate.
- Error distribution.
- Recovery rate.
- Agent-wise performance.
- Human annotation statistics.

For a more advanced version, include error detection precision and recall using deliberately injected failures with known ground-truth labels.

### K. Database

**Simple explanation:**

The application needs a place to remember everything that happened.

If a user closes the application and opens it again, previously recorded missions and annotations should still be available.

**Technical implementation:**

Use SQLite for the MVP.

Suggested database entities:

- Missions
- Agents
- Tasks
- Trajectories
- Trajectory Events
- Errors
- Annotations
- Evaluations

### PART 2 — FINAL DELIVERABLES

The backend developer must provide:

1. Working FastAPI application.
2. Agent manager for three agents.
3. Mission and task scheduler.
4. PyBullet simulation environment.
5. Robot movement and navigation logic.
6. Collision detection.
7. RoboTrace trajectory recorder.
8. AgentGuard evaluation module.
9. Error classification system.
10. Annotation manager.
11. Analytics and metrics calculations.
12. SQLite database.
13. REST APIs and WebSocket updates.

The main goal is to deliver a backend that can execute a mission, record the actions, detect failures, and send structured information to the frontend.

---

# 5. FINAL TECHNOLOGY STACK

Both members must follow this agreed technology stack.

## FRONTEND — TEAM MEMBER 1

| Technology | Purpose |
|---|---|
| React | Build the user interface |
| Vite | Frontend development setup |
| JavaScript | Frontend programming |
| Three.js | Render the 3D environment |
| React Three Fiber | Integrate Three.js with React |
| Drei | Camera, lighting and 3D helpers |
| Tailwind CSS | Application styling |
| React Router | Navigate between pages |
| Recharts | Display analytics charts |
| Lucide React | Icons |

## BACKEND — TEAM MEMBER 2

| Technology | Purpose |
|---|---|
| Python | Backend and agent logic |
| FastAPI | API development |
| PyBullet | Physics-based robotics simulation |
| WebSockets | Live simulation updates |
| SQLite | Store project data |
| SQLAlchemy or sqlite3 | Database operations |
| NumPy | Numerical calculations, if needed |

## Communication

- REST APIs: For mission creation, agent data, trajectories, errors, annotations and analytics.
- WebSockets: For continuous robot position and status updates.

## Important development decision

For the first version, do not introduce ROS 2, complex LLM agent frameworks, PostgreSQL, or distributed microservices.

They can be considered in later versions.

PyBullet should be used as the actual physics simulation if integration works within the available time. If it becomes a major blocker, the fallback is a simplified Python kinematic simulation. The application should retain the same API contract so that the frontend does not need to be rewritten.

---

# 6. HOW BOTH PARTS WILL CONNECT

This is the most important part of collaborative development.

Both members will create their respective parts independently, but they must agree on how the two applications communicate.

The frontend should not have to understand the internal Python code. It only needs to receive structured information from the backend.

## Complete communication flow

1. The user clicks Start Mission in the React application.
2. React sends the mission details to FastAPI.
3. FastAPI sends the mission to the Python task scheduler.
4. The scheduler assigns tasks to Atlas, Nova and Titan.
5. Python agents execute their assigned policies.
6. PyBullet updates the simulated robot positions and physical events.
7. RoboTrace records the actions and outcomes.
8. AgentGuard evaluates the recorded events.
9. FastAPI sends live position and status updates to React through WebSockets.
10. React updates the 3D robot models and application interface.
11. The frontend displays detected errors.
12. The human reviewer submits an annotation.
13. The backend saves the annotation in SQLite.
14. Analytics are calculated and displayed in React.

## Example: Robot position update

The Python backend can send:

{
  "mission_id": "MISSION-001",
  "agent_id": "ATLAS",
  "position": {
    "x": 4.2,
    "y": 0.5,
    "z": 2.1
  },
  "rotation": 1.57,
  "status": "MOVING",
  "current_step": 3,
  "action": "MOVE_FORWARD"
}

The React frontend reads this information and updates Atlas's 3D position.

## Example: Detected error

The backend can send:

{
  "agent_id": "ATLAS",
  "step_id": 3,
  "error_type": "COLLISION",
  "severity": "HIGH",
  "description": "Robot collided with Shelf A",
  "status": "PENDING_REVIEW"
}

The frontend displays this information on the AgentGuard page.

These examples define the expected communication format. Both members must agree on the field names and data types before implementation.

---

# 7. API CONTRACT — COMMON RESPONSIBILITY

Both members must follow the same API contract.

The backend developer implements these endpoints, and the frontend developer consumes them.

| Method | Endpoint | Responsibility |
|---|---|---|
| GET | /api/agents | Fetch all agents |
| GET | /api/missions | Fetch missions |
| POST | /api/missions | Create a mission |
| POST | /api/missions/{id}/start | Start a mission |
| POST | /api/missions/{id}/pause | Pause a mission |
| POST | /api/missions/{id}/reset | Reset a mission |
| GET | /api/missions/{id}/trajectory | Fetch trajectory events |
| GET | /api/errors | Fetch detected errors |
| POST | /api/annotations | Submit human annotation |
| GET | /api/analytics | Fetch performance metrics |
| WS | /ws/simulation | Receive live simulation updates |

Both members should create an API_CONTRACT.md file in the shared repository containing the final request and response structures.

---

# 8. GITHUB REPOSITORY STRUCTURE

Create one shared GitHub repository named:

RoboTrace-3D

The repository should have the following structure:

RoboTrace-3D/
│
├── frontend/                # Team Member 1
│   ├── public/
│   │   └── models/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── simulation/
│   │   │   └── dashboard/
│   │   ├── pages/
│   │   ├── context/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── backend/                 # Team Member 2
│   ├── agents/
│   │   ├── atlas.py
│   │   ├── nova.py
│   │   └── titan.py
│   ├── engine/
│   │   ├── simulation.py
│   │   ├── navigation.py
│   │   ├── task_scheduler.py
│   │   └── world_state.py
│   ├── robotrace/
│   │   └── trajectory_recorder.py
│   ├── agentguard/
│   │   ├── agent_guard.py
│   │   └── error_classifier.py
│   ├── annotations/
│   │   └── annotation_manager.py
│   ├── analytics/
│   │   └── metrics.py
│   ├── database/
│   │   └── db.py
│   ├── main.py
│   └── requirements.txt
│
├── docs/
│   └── API_CONTRACT.md
│
└── README.md

The frontend and backend developers should avoid modifying each other's folders unless they have discussed it first.

## Branch strategy

Use one shared repository with separate development branches:

- main
- frontend-development
- backend-development

Each member commits and pushes changes to their respective branch.

Once the modules are ready, merge both branches into main and test the complete application.

---

# 9. HOW TO WORK SIMULTANEOUSLY WITHOUT WAITING FOR EACH OTHER

This is important because both members have limited development time.

Do not wait for the other person to finish their entire part.

Use mock data and agreed API structures from the beginning.

### Frontend developer

Can start building the 3D warehouse using sample robot positions.

For example, Atlas can initially move using temporary mock data. Once the Python backend is ready, replace the mock data with actual WebSocket updates.

### Backend developer

Can build and test the FastAPI endpoints independently.

The backend developer can use Postman or Swagger UI to verify that mission creation, task execution, trajectory recording and error detection work before connecting the frontend.

### Integration

Both members should test one small connection early:

- Backend starts.
- Frontend starts.
- React successfully requests the agent list from FastAPI.
- React receives a robot position update.

Do this before implementing every feature. It will reduce integration problems later.

---

# 10. ONE-DAY DEVELOPMENT PLAN

This is an aggressive 24-hour target. The goal is to deliver a functional prototype, not a production-ready robotics platform.

| Time | Team Member 1 — Frontend | Team Member 2 — Backend |
|---|---|---|
| 0–2 hours | React setup, navigation and layout | FastAPI setup, SQLite and API contract |
| 2–5 hours | 3D warehouse and robot models | Agent manager and simulation setup |
| 5–8 hours | Robot visualization and controls | Atlas movement, task execution and navigation |
| 8–11 hours | Mission interface and live updates | Nova and Titan task policies |
| 11–14 hours | Trajectory timeline and replay | RoboTrace event recording |
| 14–17 hours | AgentGuard interface | Error detection and classification |
| 17–20 hours | Annotation and analytics pages | Annotation storage and evaluation metrics |
| 20–22 hours | API integration and bug fixing | WebSocket integration and testing |
| 22–24 hours | Final UI polish and demo | Backend testing and demo preparation |

### If time becomes limited, prioritize these features:

1. One working robot completing a warehouse task.
2. A visible 3D environment.
3. Complete trajectory recording.
4. At least two deliberately injected errors.
5. AgentGuard detecting those errors.
6. Human annotation and correction.
7. Basic multi-agent demonstration.
8. Analytics dashboard.

It is better to demonstrate a complete working workflow than to show three robots moving without meaningful functionality.

---

# 11. EXPECTED FINAL DEMONSTRATION

The final presentation should follow one continuous scenario.

**First:** Open the Overview page and introduce Atlas, Nova and Titan.

**Second:** Open the Simulation page and create a warehouse mission.

**Third:** Start the mission and demonstrate the robots performing their assigned tasks.

**Fourth:** Trigger a deliberate error, such as Atlas colliding with a shelf.

**Fifth:** Open Trajectories and replay Atlas's action sequence.

**Sixth:** Open AgentGuard and demonstrate that the system detected the incorrect action.

**Seventh:** Open Annotations and show how a human reviewer verifies or corrects the suggested label.

**Eighth:** Open Analytics and show the mission results and agent performance.

### Expected outcome

The audience should understand that RoboTrace 3D is not simply a robot animation application. It is a platform that records, evaluates, and audits autonomous agent behaviour.

---

# 12. IMPORTANT PROJECT RULES FOR BOTH TEAM MEMBERS

1. Both developers must agree on the API contract before implementation.
2. Both should use the same agent IDs: ATLAS, NOVA and TITAN.
3. All robot coordinates must follow the same coordinate convention.
4. The backend simulation is the source of truth for robot positions and task outcomes.
5. The frontend is responsible for displaying the simulation state.
6. RoboTrace records actions in chronological order.
7. AgentGuard independently evaluates actual events and task conditions.
8. Human reviewers must be able to correct automatically suggested error labels.
9. Human annotations must be saved without overwriting the original detected label.
10. All performance metrics must be calculated from actual recorded events. Any sample dashboard numbers must be clearly identified as illustrative.

---

# 13. FINAL PROJECT OBJECTIVE

RoboTrace 3D aims to bridge the gap between robotic simulation and AI agent evaluation.

It enables us to understand not only whether an autonomous agent completes a task, but also how it performs, where it fails, and how human feedback can help improve its future decisions.

**RoboTrace records the journey. AgentGuard evaluates the decisions. Human reviewers validate the results.**

Together, these modules create a complete robotic agent monitoring and decision-auditing platform.
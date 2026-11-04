# RoboTrace 3D

RoboTrace 3D is an industrial robotics tracing, 3D simulation, and autonomous safety evaluation platform. It provides high-fidelity warehouse simulation, step-by-step trajectory recording, and the AgentGuard™ 9-category error taxonomy evaluation engine with human-in-the-loop ground truth annotation.

---

## Architecture Overview

The repository is organized into a clean, modular three-tier structure:

```
RobotRace/
├── backend/                  # All Python backend, simulation, database, & tests
│   ├── agentguard/           # AgentGuard autonomous safety auditing & classification
│   ├── agents/               # Multi-agent implementations (Atlas, Nova, Titan)
│   ├── annotations/          # Human-in-the-loop ground truth management
│   ├── api/                  # FastAPI REST routes and WebSocket handlers
│   ├── app/                  # Application configuration & health routers
│   ├── database/             # SQLite async database, schema, & ORM models
│   ├── engine/               # Physics simulation (PyBullet), A* navigation, world state
│   ├── robotrace/            # Trajectory recording, cognitive state auditing
│   ├── tests/                # Comprehensive test suite (52 unit/integration tests)
│   ├── demo_robot_movement.py# Standalone PyBullet physics & navigation demo
│   ├── main.py               # FastAPI application entry point
│   ├── pytest.ini            # Pytest configuration
│   ├── requirements.txt      # Python dependencies
│   └── verify_full_system.py # 16-subsystem automated end-to-end audit
│
├── frontend/                 # React 19 + Vite + Tailwind CSS 3D dashboard
│   ├── public/               # Static assets & icons
│   ├── src/
│   │   ├── components/       # Common, layout, and 3D simulation components
│   │   ├── context/          # React context & fleet state providers
│   │   ├── data/             # Domain mock data & taxonomy definitions
│   │   ├── hooks/            # Custom hooks (`useFleet`)
│   │   ├── pages/            # 6 core dashboards (Overview, Simulation, Trajectories, etc.)
│   │   ├── services/         # API abstraction & WebSocket client layer
│   │   └── styles/           # Tailwind CSS v4 design system
│   └── package.json          # Node dependencies and scripts
│
├── docs/                     # Project documentation
│   ├── API_CONTRACT.md       # Complete REST & WebSocket API specification
│   └── design.md             # Complete architectural design specification
│
├── .gitignore                # Repository-wide Git ignore rules
└── README.md                 # Project documentation & instructions
```

---

## Getting Started

### 1. Frontend (React 19 + Vite + Three.js)

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend dashboard will be available at **`http://localhost:5173`**.

Available pages:
- **Overview (`/`)**: High-level fleet monitoring, active missions, and metric cards.
- **Simulation (`/simulation`)**: Interactive 3D warehouse studio with custom robot models (Atlas, Nova, Titan).
- **Trajectories (`/trajectories`)**: Step-by-step playback scrubber and planned vs. executed waypoint audits.
- **AgentGuard (`/agentguard`)**: 9-category failure taxonomy matrix, active safety invariants, and detected errors.
- **Annotations (`/annotations`)**: Human-in-the-loop audit studio for verifying or correcting AI classifications.
- **Analytics (`/analytics`)**: Reliability KPIs, success vs. failure distributions, and agreement benchmarks.

---

### 2. Backend (FastAPI + PyBullet + SQLite)

```bash
# Navigate to the backend directory
cd backend

# Create and activate a Python virtual environment (Python 3.10+)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`
- **Alternative Documentation (ReDoc)**: `http://localhost:8000/redoc`
- **Live WebSocket Telemetry**: `ws://localhost:8000/ws/telemetry`

---

### 3. Verification & Testing

#### Run Backend Unit & Integration Tests (52 tests)
```bash
cd backend
pytest
```

#### Run Full 16-Subsystem Verification Audit
```bash
cd backend
python verify_full_system.py
```

#### Run PyBullet Physics & A* Movement Demo
```bash
cd backend
python demo_robot_movement.py
```

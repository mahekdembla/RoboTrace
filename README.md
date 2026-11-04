# RoboTrace 3D

A 3D robotics simulation and tracing platform.

## Tech Stack

- **Backend:** FastAPI (Python 3.14)
- **Database:** SQLite (dev) with async SQLAlchemy ORM
- **API Docs:** Auto-generated at `/docs` (Swagger) and `/redoc`

## Getting Started

### Prerequisites
- Python 3.14+

### Setup

```bash
# Navigate to project root
cd RoboTrace

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
RoboTrace/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # App settings & configuration
│   ├── database.py           # SQLAlchemy engine & session
│   ├── models/               # SQLAlchemy ORM models
│   │   └── __init__.py
│   ├── schemas/              # Pydantic request/response schemas
│   │   └── __init__.py
│   ├── routers/              # API route handlers
│   │   └── __init__.py
│   ├── services/             # Business logic layer
│   │   └── __init__.py
│   └── utils/                # Shared utilities & helpers
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```


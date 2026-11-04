"""Top-level main entry point forwarding to backend.main.

Allows running `uvicorn main:app --reload` from the repository root as well
as from the `backend/` directory.
"""

from backend.main import app

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)


"""FitBuddy Root Entrypoint for Vercel and ASGI runners."""

import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app


if __name__ == "__main__":
    import uvicorn

    print("=" * 55)
    print("FitBuddy is running!")
    print("Open in your browser: http://localhost:8000")
    print("=" * 55)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
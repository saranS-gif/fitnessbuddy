"""FitBuddy Root Entrypoint for Vercel and ASGI runners."""
import sys
from pathlib import Path

# Add backend directory to sys.path so 'app' package is discovered
BACKEND_DIR = Path(__file__).resolve().parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 55)
    print("  FitBuddy is running!")
    print("  Open in your browser:  http://localhost:8000")
    print("=" * 55 + "\n")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

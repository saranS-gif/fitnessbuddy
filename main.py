"""FitBuddy Root Entrypoint for Vercel and ASGI runners."""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 55)
    print("  FitBuddy is running!")
    print("  Open in your browser:  http://localhost:8000")
    print("=" * 55 + "\n")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

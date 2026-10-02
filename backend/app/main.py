import os
import json
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db
from app.models import User, WorkoutPlan
from app.schemas import UserCreate, FeedbackRequest, MarkCompleteRequest
from app.services.workout_service import WorkoutService
from app.ai.gemini import get_gemini_model

logger = logging.getLogger("fitbuddy")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[FitBuddy] Starting application...")
    init_db()
    # Check Gemini config
    get_gemini_model()
    print("[FitBuddy] Server running")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="FitBuddy — Simple AI Personal Fitness Companion",
    version="2.0.0",
    lifespan=lifespan
)

from pathlib import Path

# Resolve frontend directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJECT_ROOT / "frontend" / "templates"
STATIC_DIR = PROJECT_ROOT / "frontend" / "static"

# Fallback to local package directory if needed
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
if not STATIC_DIR.exists():
    STATIC_DIR = Path(__file__).resolve().parent / "static"

STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.middleware("http")
async def ensure_localhost_middleware(request: Request, call_next):
    # Firebase Auth requires 'localhost' rather than '127.0.0.1' by default when testing locally.
    # Automatically redirect any 127.0.0.1 requests to localhost in local dev.
    host = request.headers.get("host", "")
    if host.startswith("127.0.0.1") and not os.environ.get("VERCEL"):
        new_url = str(request.url).replace("127.0.0.1", "localhost", 1)
        return RedirectResponse(url=new_url, status_code=307)
    return await call_next(request)


# ==========================================
# PAGE ROUTES (Jinja2 HTML)
# ==========================================

@app.get("/", response_class=HTMLResponse)
def page_landing(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/onboarding", response_class=HTMLResponse)
def page_onboarding(request: Request):
    return templates.TemplateResponse(request=request, name="onboarding.html")


@app.get("/loading", response_class=HTMLResponse)
def page_loading(request: Request):
    return templates.TemplateResponse(request=request, name="loading.html")


@app.get("/dashboard", response_class=HTMLResponse)
def page_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")


@app.get("/workout", response_class=HTMLResponse)
def page_workout(request: Request):
    return templates.TemplateResponse(request=request, name="workout.html")


@app.get("/feedback", response_class=HTMLResponse)
def page_feedback(request: Request):
    return templates.TemplateResponse(request=request, name="feedback.html")


@app.get("/history", response_class=HTMLResponse)
def page_history(request: Request):
    return templates.TemplateResponse(request=request, name="history.html")


@app.get("/admin", response_class=HTMLResponse)
def page_admin(request: Request, db: Session = Depends(get_db)):
    users = WorkoutService.list_users(db)
    total_plans = db.query(WorkoutPlan).count()
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "users": users,
            "total_users": len(users),
            "total_plans": total_plans
        }
    )


# ==========================================
# API ENDPOINTS
# ==========================================

@app.post("/api/generate")
def api_generate(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Main Plan Generation Endpoint:
    1. Validates user data
    2. Saves User
    3. Calls Gemini AI (with deterministic fallback)
    4. Saves plan & revision
    5. Returns structured response
    """
    try:
        user = WorkoutService.create_user(db, user_data)
        plan_obj = WorkoutService.generate_and_save_plan(db, user)

        try:
            active_plan = json.loads(plan_obj.original_plan)
        except Exception:
            active_plan = {}

        return {
            "success": True,
            "user_id": user.id,
            "plan_id": plan_obj.id,
            "plan": active_plan
        }
    except Exception as e:
        logger.error(f"Plan generation failed: {e}", exc_info=True)
        print(f"[FitBuddy] Plan generation failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": f"Unable to generate your plan: {str(e)}"
            }
        )



@app.post("/api/feedback")
def api_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Applies user feedback to a plan:
    Preserves original_plan; saves new PlanRevision and updates updated_plan.
    """
    try:
        plan_obj = WorkoutService.update_plan_with_feedback(db, req.plan_id, req.feedback)
        updated_plan = json.loads(plan_obj.updated_plan) if plan_obj.updated_plan else {}
        return {
            "success": True,
            "plan_id": plan_obj.id,
            "plan": updated_plan
        }
    except Exception as e:
        logger.error(f"Feedback application failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Unable to update your plan with feedback."
            }
        )


@app.get("/api/plan/{plan_id}")
def api_get_plan(plan_id: int, db: Session = Depends(get_db)):
    """Retrieves workout plan by ID."""
    plan_obj = WorkoutService.get_plan(db, plan_id)
    if not plan_obj:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "Workout plan not found"}
        )

    try:
        orig = json.loads(plan_obj.original_plan) if plan_obj.original_plan else {}
    except Exception:
        orig = {}

    try:
        upd = json.loads(plan_obj.updated_plan) if plan_obj.updated_plan else None
    except Exception:
        upd = None

    try:
        completed = json.loads(plan_obj.completed_days) if plan_obj.completed_days else []
    except Exception:
        completed = []

    return {
        "success": True,
        "id": plan_obj.id,
        "user_id": plan_obj.user_id,
        "original_plan": orig,
        "updated_plan": upd,
        "active_plan": upd or orig,
        "completed_days": completed,
        "created_at": plan_obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if plan_obj.created_at else ""
    }


@app.get("/api/history/{user_id}")
def api_get_history(user_id: int, db: Session = Depends(get_db)):
    """Retrieves complete revision history for a user's latest plan."""
    plan_obj = WorkoutService.get_latest_plan_for_user(db, user_id)
    if not plan_obj:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "No workout plan found for this user"}
        )

    history = WorkoutService.get_plan_history(db, plan_obj.id)
    return {
        "success": True,
        "plan_id": plan_obj.id,
        "user_id": user_id,
        "history": history
    }


@app.post("/api/plan/{plan_id}/complete")
def api_mark_complete(plan_id: int, req: MarkCompleteRequest, db: Session = Depends(get_db)):
    """Marks a specific day as completed or uncompleted."""
    completed_days = WorkoutService.toggle_day_completion(db, plan_id, req.day, req.completed)
    return {
        "success": True,
        "day": req.day,
        "completed": req.completed,
        "completed_days": completed_days
    }


# Register API routers
from app.routes.user_routes import router as user_router
app.include_router(user_router)


@app.post("/admin/delete/{user_id}")
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    """Deletes a user and their plans."""
    WorkoutService.delete_user(db, user_id)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "FitBuddy AI"}

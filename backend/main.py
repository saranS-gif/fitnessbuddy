import os
import json
import logging
from datetime import datetime, timezone
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
if not STATIC_DIR.exists():
    STATIC_DIR = Path(__file__).resolve().parent / "static"

STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


from fastapi.middleware.cors import CORSMiddleware

# Enable CORS for decoupled deployment (e.g. Vercel frontend calling Render backend API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
@app.get("/feedback/", response_class=HTMLResponse)
def page_feedback(request: Request):
    return templates.TemplateResponse(request=request, name="feedback.html")


@app.get("/comparison", response_class=HTMLResponse)
@app.get("/comparison/", response_class=HTMLResponse)
@app.get("/plan-comparison", response_class=HTMLResponse)
@app.get("/plan-comparison/", response_class=HTMLResponse)
@app.get("/feedback/updated-plan", response_class=HTMLResponse)
@app.get("/feedback/updated-plan/", response_class=HTMLResponse)
def page_comparison(request: Request):
    return templates.TemplateResponse(request=request, name="comparison.html")


@app.get("/history", response_class=HTMLResponse)
@app.get("/history/", response_class=HTMLResponse)
def page_history(request: Request):
    return templates.TemplateResponse(request=request, name="history.html")


@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/", response_class=HTMLResponse)
@app.get("/admin-portal", response_class=HTMLResponse)
@app.get("/admin-portal/", response_class=HTMLResponse)
@app.get("/portal", response_class=HTMLResponse)
@app.get("/portal/", response_class=HTMLResponse)
@app.get("/admin/dashboard", response_class=HTMLResponse)
@app.get("/admin/dashboard/", response_class=HTMLResponse)
def page_admin(request: Request, db: Session = Depends(get_db)):
    users = WorkoutService.list_users(db)
    total_plans = db.query(WorkoutPlan).count()
    
    users_data = []
    for u in users:
        plan_id = None
        plan_summary = ""
        days_count = 0
        latest_plan = None
        if hasattr(u, "plans") and u.plans:
            latest_plan = u.plans[0]
        elif hasattr(u, "workout_plans") and u.workout_plans:
            latest_plan = u.workout_plans[0]
            
        if latest_plan:
            plan_id = latest_plan.id
            try:
                p_content = json.loads(latest_plan.updated_plan or latest_plan.original_plan)
                plan_summary = p_content.get("summary", "Custom AI Regimen")
                days_count = len(p_content.get("days", []))
            except Exception:
                plan_summary = "Custom Workout"
                days_count = 7
                
        users_data.append({
            "id": u.id,
            "name": u.name,
            "age": u.age,
            "weight": u.weight,
            "height": getattr(u, "height", 170.0),
            "goal": u.goal,
            "intensity": u.intensity,
            "experience": getattr(u, "experience", "Intermediate"),
            "location": getattr(u, "location", getattr(u, "workout_location", "Home")),
            "preferred_days": u.preferred_days,
            "created_at": u.created_at.strftime("%b %d, %Y") if getattr(u, "created_at", None) else "Recent",
            "plan_id": plan_id,
            "plan_summary": plan_summary,
            "days_count": days_count
        })

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "users": users,
            "users_json": json.dumps(users_data),
            "total_users": len(users),
            "total_plans": total_plans,
            "gemini_active": bool(settings.GEMINI_API_KEY),
            "gemini_model": settings.GEMINI_MODEL,
            "db_type": "SQLite Telemetry",
            "app_version": "2.0.0"
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
        orig_plan = json.loads(plan_obj.original_plan) if plan_obj.original_plan else {}
        return {
            "success": True,
            "plan_id": plan_obj.id,
            "plan": updated_plan,
            "original_plan": orig_plan,
            "feedback": req.feedback
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


@app.get("/admin/export")
def admin_export_data(db: Session = Depends(get_db)):
    """Exports all athlete records and their workout plans as JSON."""
    users = WorkoutService.list_users(db)
    export_payload = []
    for u in users:
        u_plans = []
        user_plan_list = getattr(u, "plans", []) or getattr(u, "workout_plans", [])
        for p in user_plan_list:
            try:
                active = json.loads(p.updated_plan or p.original_plan)
            except Exception:
                active = {}
            u_plans.append({
                "plan_id": p.id,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "plan": active
            })
        export_payload.append({
            "id": u.id,
            "name": u.name,
            "age": u.age,
            "weight": u.weight,
            "height": getattr(u, "height", 170.0),
            "goal": u.goal,
            "intensity": u.intensity,
            "experience": getattr(u, "experience", "Intermediate"),
            "location": getattr(u, "location", "Home"),
            "preferred_days": u.preferred_days,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "plans": u_plans
        })
    return JSONResponse(
        content={"athletes": export_payload, "exported_at": datetime.now(timezone.utc).isoformat()},
        headers={"Content-Disposition": "attachment; filename=fitbuddy_athletes_export.json"}
    )


@app.get("/health")
def health():
    return {"status": "healthy", "service": "FitBuddy AI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

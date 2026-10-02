import os
import json
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.admin_service import AdminService
from app.services.workout_service import WorkoutService
from app.services.user_service import UserService
from app.dependencies import get_current_admin
from app.models.admin import Admin
from typing import Optional

from pathlib import Path

# Resolve frontend templates directory
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_TEMPLATES_DIR = _PROJECT_ROOT / "frontend" / "templates"
if not _TEMPLATES_DIR.exists():
    _TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

router = APIRouter(include_in_schema=False)


# --- Public Pages ---
@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("public/landing.html", {"request": request})


@router.get("/how-it-works", response_class=HTMLResponse)
def how_it_works(request: Request):
    return templates.TemplateResponse("public/how-it-works.html", {"request": request})


# --- Onboarding Wizard ---
@router.get("/onboarding", response_class=HTMLResponse)
@router.get("/onboarding/profile", response_class=HTMLResponse)
def onboarding(request: Request):
    return templates.TemplateResponse("onboarding/profile.html", {"request": request})


@router.get("/onboarding/goals", response_class=HTMLResponse)
def onboarding_goals(request: Request):
    return templates.TemplateResponse("onboarding/goals.html", {"request": request})


@router.get("/onboarding/preferences", response_class=HTMLResponse)
def onboarding_preferences(request: Request):
    return templates.TemplateResponse("onboarding/preferences.html", {"request": request})


@router.get("/onboarding/review", response_class=HTMLResponse)
def onboarding_review(request: Request):
    return templates.TemplateResponse("onboarding/review.html", {"request": request})


# --- User Dashboard Pages ---
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard/dashboard.html", {"request": request})


@router.get("/dashboard/workout", response_class=HTMLResponse)
def dashboard_workout(request: Request):
    return templates.TemplateResponse("dashboard/workout.html", {"request": request})


@router.get("/dashboard/daily-workout", response_class=HTMLResponse)
def daily_workout(request: Request):
    return templates.TemplateResponse("dashboard/daily-workout.html", {"request": request})


@router.get("/dashboard/nutrition", response_class=HTMLResponse)
def dashboard_nutrition(request: Request):
    return templates.TemplateResponse("dashboard/nutrition.html", {"request": request})


@router.get("/dashboard/history", response_class=HTMLResponse)
def dashboard_history(request: Request):
    return templates.TemplateResponse("dashboard/history.html", {"request": request})


@router.get("/dashboard/profile", response_class=HTMLResponse)
def dashboard_profile(request: Request):
    return templates.TemplateResponse("dashboard/profile.html", {"request": request})


# --- Feedback & Comparison Pages ---
@router.get("/feedback", response_class=HTMLResponse)
def feedback(request: Request):
    return templates.TemplateResponse("feedback/feedback.html", {"request": request})


@router.get("/feedback/updated-plan", response_class=HTMLResponse)
def updated_plan_comparison(request: Request):
    return templates.TemplateResponse("feedback/updated-plan.html", {"request": request})


# --- Admin Interface ---
@router.get("/admin/login", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@router.get("/admin/users", response_class=HTMLResponse)
def admin_users(request: Request):
    return templates.TemplateResponse("admin/users.html", {"request": request})


@router.get("/admin/user-detail", response_class=HTMLResponse)
def admin_user_detail(request: Request):
    return templates.TemplateResponse("admin/user-detail.html", {"request": request})


@router.get("/admin/plan-comparison", response_class=HTMLResponse)
def admin_plan_comparison(request: Request):
    return templates.TemplateResponse("admin/plan-comparison.html", {"request": request})

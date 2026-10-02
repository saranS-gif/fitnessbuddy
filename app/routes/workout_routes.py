import json
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.user_service import UserService
from app.services.workout_service import WorkoutService
from app.schemas.workout import (
    WorkoutPlanOut, WeeklyWorkoutPlan, NutritionGuidance, MarkCompleteRequest
)
from app.schemas.feedback import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/api/workouts", tags=["Workouts"])


class GenerateRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user to generate a plan for")


def _format_plan_response(plan) -> Dict[str, Any]:
    """Helper to convert stored JSON strings to proper schema dict for output."""
    try:
        original_dict = json.loads(plan.original_plan) if plan.original_plan else {}
    except Exception:
        original_dict = {}

    try:
        updated_dict = json.loads(plan.updated_plan) if plan.updated_plan else None
    except Exception:
        updated_dict = None
    
    nutrition_obj = None
    if plan.nutrition_tip:
        try:
            nutrition_obj = json.loads(plan.nutrition_tip)
        except Exception:
            nutrition_obj = plan.nutrition_tip

    completed_days_list = []
    if plan.completed_days:
        try:
            completed_days_list = json.loads(plan.completed_days)
        except Exception:
            completed_days_list = []

    return {
        "id": plan.id,
        "user_id": plan.user_id,
        "original_plan": original_dict,
        "updated_plan": updated_dict,
        "nutrition_tip": nutrition_obj,
        "recovery_tip": plan.recovery_tip,
        "completed_days": completed_days_list,
        "created_at": plan.created_at,
        "updated_at": plan.updated_at
    }


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_workout(req: GenerateRequest, db: Session = Depends(get_db)):
    """Generate 7-day personalized workout plan and nutrition guidance via Gemini AI."""
    user = UserService.get_by_id(db, req.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please complete onboarding first."
        )
    try:
        plan = WorkoutService.generate_and_save_plan(db, user)
        return _format_plan_response(plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plan generation failed: {str(e)}"
        )


@router.get("/{user_id}")
def get_user_latest_plan(user_id: int, db: Session = Depends(get_db)):
    """Retrieve the latest workout plan for a specific user."""
    plan = WorkoutService.get_latest_user_plan(db, user_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No workout plan found for this user."
        )
    return _format_plan_response(plan)


@router.get("/plan/{plan_id}")
def get_plan_by_id(plan_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific plan by its Plan ID."""
    plan = WorkoutService.get_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found."
        )
    return _format_plan_response(plan)


@router.post("/{plan_id}/feedback")
def submit_plan_feedback(
    plan_id: int,
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Submits user feedback on a plan.
    Triggers Gemini AI update.
    The original plan is preserved intact, and an updated plan is created.
    """
    plan = WorkoutService.get_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found."
        )
    try:
        updated_plan_obj = WorkoutService.update_plan_with_feedback(
            db=db,
            plan_id=plan_id,
            feedback_text=feedback_in.feedback_text
        )
        return {
            "message": "Your plan has been updated based on your feedback.",
            "plan": _format_plan_response(updated_plan_obj)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not update plan with feedback: {str(e)}"
        )


@router.get("/{plan_id}/history")
def get_plan_history(plan_id: int, db: Session = Depends(get_db)):
    """Retrieve complete revision timeline for this workout plan."""
    plan = WorkoutService.get_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found."
        )
    history = WorkoutService.get_plan_history(db, plan_id)
    return {
        "plan_id": plan_id,
        "history": history
    }


@router.post("/{plan_id}/complete")
def complete_day(
    plan_id: int,
    req: MarkCompleteRequest,
    db: Session = Depends(get_db)
):
    """Mark a specific day as completed or uncompleted."""
    plan = WorkoutService.get_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found."
        )
    completed_days = WorkoutService.set_day_completion(db, plan_id, req.day, req.completed)
    return {
        "plan_id": plan_id,
        "day": req.day,
        "completed": req.completed,
        "completed_days": completed_days
    }

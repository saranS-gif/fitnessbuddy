from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.admin_service import AdminService
from app.services.workout_service import WorkoutService
from app.utils.security import create_access_token
from app.dependencies import require_admin, get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class AdminLoginInput(BaseModel):
    username: str = Field(..., min_length=2)
    password: str = Field(..., min_length=4)


@router.post("/login")
def admin_login(creds: AdminLoginInput, response: Response, db: Session = Depends(get_db)):
    """Authenticates admin and issues session JWT."""
    admin = AdminService.authenticate(db, creds.username, creds.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrator credentials"
        )
    token = create_access_token({
        "sub": str(admin.id),
        "username": admin.username,
        "is_admin": True
    })
    response.set_cookie(
        key="fitbuddy_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=86400 * 7,
        samesite="lax"
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": admin.username
    }


@router.get("/stats")
def get_stats(
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrieve real-time database telemetry (never fabricated)."""
    return AdminService.get_real_stats(db)


@router.get("/users")
def get_users(
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrieve directory of registered users."""
    users = AdminService.list_users(db)
    result = []
    for u in users:
        active_plan = WorkoutService.get_latest_user_plan(db, u.id)
        plan_status = "No Plan"
        if active_plan:
            plan_status = "Plan Updated" if active_plan.updated_plan else "Original Plan Active"
        result.append({
            "id": u.id,
            "name": u.name,
            "age": u.age,
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "experience": u.experience,
            "workout_location": u.workout_location,
            "created_at": u.created_at,
            "plan_status": plan_status
        })
    return result


@router.get("/users/{user_id}")
def get_user_dossier(
    user_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrieve complete dossier for an individual user."""
    dossier = AdminService.get_user_dossier(db, user_id)
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user = dossier["user"]
    plans_list = []
    for p in dossier["plans"]:
        history = WorkoutService.get_plan_history(db, p.id)
        plans_list.append({
            "id": p.id,
            "created_at": p.created_at,
            "has_updated_plan": p.updated_plan is not None,
            "history": history
        })

    feedbacks_list = [
        {
            "id": f.id,
            "plan_id": f.workout_plan_id,
            "feedback_text": f.feedback_text,
            "created_at": f.created_at
        } for f in dossier["feedbacks"]
    ]

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "experience": user.experience,
            "workout_location": user.workout_location,
            "created_at": user.created_at
        },
        "plans": plans_list,
        "feedbacks": feedbacks_list
    }


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user and cascade their plans and feedback."""
    success = AdminService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": f"User {user_id} successfully deleted."}

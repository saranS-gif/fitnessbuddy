from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackOut
from app.services.feedback_service import FeedbackService
from app.services.workout_service import WorkoutService
from app.models.feedback import Feedback

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_feedback_standalone(
    plan_id: int,
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db)
):
    plan = WorkoutService.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout plan not found")
    
    WorkoutService.update_plan_with_feedback(db, plan_id, feedback_in.feedback_text)
    latest_feedback = (
        db.query(Feedback)
        .filter(Feedback.workout_plan_id == plan_id)
        .order_by(Feedback.id.desc())
        .first()
    )
    if not latest_feedback:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Feedback recording error")
    return latest_feedback


@router.get("/plan/{plan_id}", response_model=List[FeedbackOut])
def get_feedbacks_for_plan(plan_id: int, db: Session = Depends(get_db)):
    return FeedbackService.get_by_plan(db, plan_id)

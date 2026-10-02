from typing import List
from sqlalchemy.orm import Session
from app.models.feedback import Feedback


class FeedbackService:
    @staticmethod
    def get_by_plan(db: Session, plan_id: int) -> List[Feedback]:
        return (
            db.query(Feedback)
            .filter(Feedback.workout_plan_id == plan_id)
            .order_by(Feedback.created_at.asc())
            .all()
        )

    @staticmethod
    def list_all(db: Session) -> List[Feedback]:
        return db.query(Feedback).order_by(Feedback.created_at.desc()).all()

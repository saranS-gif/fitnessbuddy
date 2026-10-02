from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.admin import Admin
from app.models.user import User
from app.models.workout import WorkoutPlan
from app.models.feedback import Feedback
from app.utils.security import verify_password


class AdminService:
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[Admin]:
        admin = db.query(Admin).filter(Admin.username == username.strip()).first()
        if not admin or not verify_password(password, admin.password_hash):
            return None
        return admin

    @staticmethod
    def get_real_stats(db: Session) -> Dict[str, int]:
        """
        Calculates exact operational metrics directly from the database.
        Never fabricates numbers.
        """
        total_users = db.query(User).count()
        plans_generated = db.query(WorkoutPlan).count()
        plans_updated = db.query(WorkoutPlan).filter(WorkoutPlan.updated_plan.isnot(None)).count()
        feedback_submitted = db.query(Feedback).count()

        return {
            "total_users": total_users,
            "plans_generated": plans_generated,
            "plans_updated": plans_updated,
            "feedback_submitted": feedback_submitted
        }

    @staticmethod
    def list_users(db: Session) -> List[User]:
        return db.query(User).order_by(User.created_at.desc()).all()

    @staticmethod
    def get_user_dossier(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        plans = (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user_id)
            .order_by(WorkoutPlan.created_at.desc())
            .all()
        )
        feedbacks = (
            db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(Feedback.created_at.desc())
            .all()
        )

        return {
            "user": user,
            "plans": plans,
            "feedbacks": feedbacks
        }

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True

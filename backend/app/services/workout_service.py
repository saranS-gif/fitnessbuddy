import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models import User, WorkoutPlan, PlanRevision, Feedback
from app.schemas import UserCreate
from app.ai.gemini import generate_workout_plan, generate_updated_plan

logger = logging.getLogger("fitbuddy")


class WorkoutService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        user = User(
            name=user_in.name.strip(),
            age=user_in.age,
            weight=user_in.weight,
            height=user_in.height,
            goal=user_in.goal,
            intensity=user_in.intensity,
            experience=user_in.experience,
            location=user_in.location,
            workout_location=user_in.location,
            equipment=user_in.equipment,
            preferred_days=json.dumps(user_in.preferred_days)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def list_users(db: Session) -> List[User]:
        return db.query(User).order_by(User.created_at.desc()).all()

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def generate_and_save_plan(db: Session, user: User) -> WorkoutPlan:
        """
        1. Formats user profile
        2. Calls Gemini AI (or fallback)
        3. Persists initial plan and Revision v1
        """
        try:
            preferred_days = json.loads(user.preferred_days) if user.preferred_days else ["Monday", "Wednesday", "Friday"]
        except Exception:
            preferred_days = ["Monday", "Wednesday", "Friday"]

        user_profile = {
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "height": user.height,
            "goal": user.goal,
            "intensity": user.intensity,
            "experience": user.experience,
            "location": user.location,
            "equipment": user.equipment,
            "preferred_days": preferred_days
        }

        # Generate plan
        plan_data = generate_workout_plan(user_profile)
        plan_json_str = json.dumps(plan_data)
        nutrition_tip_str = json.dumps(plan_data.get("nutrition", {}))
        recovery_tip_str = plan_data.get("disclaimer", "")

        db_plan = WorkoutPlan(
            user_id=user.id,
            original_plan=plan_json_str,
            updated_plan=None,
            nutrition_tip=nutrition_tip_str,
            recovery_tip=recovery_tip_str,
            completed_days="[]"
        )
        db.add(db_plan)
        db.flush()

        revision_1 = PlanRevision(
            workout_plan_id=db_plan.id,
            version_number=1,
            plan_data=plan_json_str,
            feedback_applied="Initial Plan Creation"
        )
        db.add(revision_1)

        db.commit()
        db.refresh(db_plan)
        print("[FitBuddy] Plan saved")
        return db_plan

    @staticmethod
    def get_plan(db: Session, plan_id: int) -> Optional[WorkoutPlan]:
        return db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()

    @staticmethod
    def get_latest_plan_for_user(db: Session, user_id: int) -> Optional[WorkoutPlan]:
        return (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user_id)
            .order_by(WorkoutPlan.created_at.desc())
            .first()
        )

    @staticmethod
    def update_plan_with_feedback(db: Session, plan_id: int, feedback_text: str) -> WorkoutPlan:
        """
        Submits feedback to Gemini without overwriting original_plan.
        Saves new revision (v2, v3, etc.) and updates plan.updated_plan.
        """
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
        if not plan:
            raise ValueError(f"Plan ID {plan_id} not found.")

        user = plan.user
        try:
            preferred_days = json.loads(user.preferred_days) if user.preferred_days else ["Monday", "Wednesday", "Friday"]
        except Exception:
            preferred_days = ["Monday", "Wednesday", "Friday"]

        user_profile = {
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "height": user.height,
            "goal": user.goal,
            "intensity": user.intensity,
            "experience": user.experience,
            "location": user.location,
            "equipment": user.equipment,
            "preferred_days": preferred_days
        }

        # Current plan data (uses latest revision or original)
        base_plan_str = plan.updated_plan if plan.updated_plan else plan.original_plan
        try:
            base_plan_dict = json.loads(base_plan_str)
        except Exception:
            base_plan_dict = {}

        # Call AI update
        updated_dict = generate_updated_plan(user_profile, base_plan_dict, feedback_text)
        updated_json_str = json.dumps(updated_dict)

        # Update updated_plan on record (original_plan is NOT touched)
        plan.updated_plan = updated_json_str

        # Save Revision
        current_revs = len(plan.revisions) if plan.revisions else 1
        new_version = current_revs + 1

        revision = PlanRevision(
            workout_plan_id=plan.id,
            version_number=new_version,
            plan_data=updated_json_str,
            feedback_applied=feedback_text
        )
        db.add(revision)

        # Record feedback
        feedback_entry = Feedback(
            workout_plan_id=plan.id,
            user_id=user.id,
            feedback_text=feedback_text
        )
        db.add(feedback_entry)

        db.commit()
        db.refresh(plan)
        print(f"[FitBuddy] Revision {new_version} saved from feedback")
        return plan

    @staticmethod
    def get_plan_history(db: Session, plan_id: int) -> List[Dict[str, Any]]:
        revisions = (
            db.query(PlanRevision)
            .filter(PlanRevision.workout_plan_id == plan_id)
            .order_by(PlanRevision.version_number.asc())
            .all()
        )
        result = []
        for r in revisions:
            try:
                p_data = json.loads(r.plan_data)
            except Exception:
                p_data = {}
            result.append({
                "id": r.id,
                "version": r.version_number,
                "feedback": r.feedback_applied,
                "plan": p_data,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
            })
        return result

    @staticmethod
    def toggle_day_completion(db: Session, plan_id: int, day: str, completed: bool) -> List[str]:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
        if not plan:
            return []

        try:
            completed_days = json.loads(plan.completed_days) if plan.completed_days else []
        except Exception:
            completed_days = []

        if completed and day not in completed_days:
            completed_days.append(day)
        elif not completed and day in completed_days:
            completed_days.remove(day)

        plan.completed_days = json.dumps(completed_days)
        db.commit()
        return completed_days

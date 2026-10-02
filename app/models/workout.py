from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.database import Base


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # JSON strings storing the structured 7-day plan
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)  # Populated when feedback is applied; original_plan is NEVER overwritten
    
    # Nutrition & Recovery guidance (JSON string or formatted text)
    nutrition_tip = Column(Text, nullable=True)
    recovery_tip = Column(Text, nullable=True)
    
    # JSON list of completed day names e.g. ["Monday", "Wednesday"]
    completed_days = Column(Text, default="[]")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="workout_plans")
    feedbacks = relationship("Feedback", back_populates="workout_plan", cascade="all, delete-orphan", order_by="Feedback.created_at.asc()")
    revisions = relationship("PlanRevision", back_populates="workout_plan", cascade="all, delete-orphan", order_by="PlanRevision.version_number.asc()")


class PlanRevision(Base):
    __tablename__ = "plan_revisions"

    id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)  # 1 for Original, 2 for First update, etc.
    plan_data = Column(Text, nullable=False)  # Complete 7-day JSON plan for this revision
    feedback_applied = Column(Text, nullable=True)  # User feedback string that prompted this revision
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    workout_plan = relationship("WorkoutPlan", back_populates="revisions")

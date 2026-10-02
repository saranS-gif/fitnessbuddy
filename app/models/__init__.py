from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=True, default=170.0)
    goal = Column(String(50), nullable=False)
    intensity = Column(String(50), nullable=False)
    experience = Column(String(50), nullable=False)
    location = Column(String(50), nullable=True, default="Home")
    workout_location = Column(String(50), nullable=True, default="Home")  # Backward compatibility
    equipment = Column(String(100), nullable=True, default="None")
    preferred_days = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan", order_by="WorkoutPlan.created_at.desc()")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)
    recovery_tip = Column(Text, nullable=True)
    completed_days = Column(Text, default="[]")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="plans")
    revisions = relationship("PlanRevision", back_populates="plan", cascade="all, delete-orphan", order_by="PlanRevision.version_number.asc()")
    feedbacks = relationship("Feedback", back_populates="plan", cascade="all, delete-orphan", order_by="Feedback.created_at.asc()")


class PlanRevision(Base):
    __tablename__ = "plan_revisions"

    id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    plan_data = Column(Text, nullable=False)
    feedback_applied = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    plan = relationship("WorkoutPlan", back_populates="revisions")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    feedback_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="feedbacks")
    plan = relationship("WorkoutPlan", back_populates="feedbacks")


__all__ = ["User", "WorkoutPlan", "PlanRevision", "Feedback"]

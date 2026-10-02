from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)  # in kg
    goal = Column(String(50), nullable=False)  # Weight Loss, Muscle Gain, General Fitness, Flexibility, General Wellness
    intensity = Column(String(50), nullable=False)  # Low, Medium, High
    experience = Column(String(50), nullable=False)  # Beginner, Intermediate, Advanced
    workout_location = Column(String(50), nullable=False)  # Home, Gym, Outdoor
    preferred_days = Column(Text, nullable=False)  # JSON-encoded array or comma-separated: ["Monday", "Wednesday", "Friday"]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    workout_plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan", order_by="WorkoutPlan.created_at.desc()")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

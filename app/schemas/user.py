from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=12, le=100)
    weight: float = Field(..., ge=20.0, le=300.0, description="Weight in kilograms")
    goal: str = Field(..., description="Weight Loss, Muscle Gain, General Fitness, Flexibility, General Wellness")
    intensity: str = Field(..., description="Low, Medium, High")
    experience: str = Field(..., description="Beginner, Intermediate, Advanced")
    workout_location: str = Field(..., description="Home, Gym, Outdoor")
    preferred_days: List[str] = Field(default_factory=lambda: ["Monday", "Wednesday", "Friday"])


class UserOut(BaseModel):
    id: int
    name: str
    age: int
    weight: float
    goal: str
    intensity: str
    experience: str
    workout_location: str
    preferred_days: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

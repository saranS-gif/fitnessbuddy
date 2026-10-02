from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=12, le=100)
    weight: float = Field(..., ge=20.0, le=300.0, description="Weight in kg")
    height: float = Field(default=170.0, ge=50.0, le=250.0, description="Height in cm")
    goal: str = Field(default="General Fitness", description="Fitness goal")
    intensity: str = Field(default="Medium", description="Low, Medium, High")
    experience: str = Field(default="Beginner", description="Beginner, Intermediate, Advanced")
    location: str = Field(default="Home", description="Home, Gym, Outdoor")
    equipment: str = Field(default="None", description="Equipment available")
    preferred_days: List[str] = Field(default_factory=lambda: ["Monday", "Wednesday", "Friday"])


class UserOut(BaseModel):
    id: int
    name: str
    age: int
    weight: float
    height: float
    goal: str
    intensity: str
    experience: str
    location: str
    equipment: str
    preferred_days: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- EXERCISE & WORKOUT SCHEMAS ---
class ExerciseSchema(BaseModel):
    name: str
    sets: int = 3
    reps: Union[int, str] = "10-12"
    rest_seconds: int = 60
    instructions: Optional[str] = None


class DayWorkoutSchema(BaseModel):
    day: str
    focus: str
    type: str = "Workout"  # "Workout" or "Rest"
    warmup: List[str] = Field(default_factory=list)
    exercises: List[ExerciseSchema] = Field(default_factory=list)
    cooldown: List[str] = Field(default_factory=list)
    recovery: str = "Ensure adequate hydration, protein, and 7-8 hours of sleep."


class NutritionGuidanceSchema(BaseModel):
    calories_guidance: str
    protein_guidance: str
    hydration: str
    tip: str


class StructuredWorkoutPlan(BaseModel):
    summary: str
    weekly_goal: str
    days: List[DayWorkoutSchema]
    nutrition: NutritionGuidanceSchema
    disclaimer: str = "General wellness guidance only. Consult a qualified professional for medical concerns."


# --- API REQUESTS & RESPONSES ---
class GenerateResponse(BaseModel):
    success: bool
    user_id: Optional[int] = None
    plan_id: Optional[int] = None
    plan: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class FeedbackRequest(BaseModel):
    plan_id: int
    feedback: str


class MarkCompleteRequest(BaseModel):
    day: str
    completed: bool


__all__ = [
    "UserCreate", "UserOut", "ExerciseSchema", "DayWorkoutSchema",
    "NutritionGuidanceSchema", "StructuredWorkoutPlan", "GenerateResponse",
    "FeedbackRequest", "MarkCompleteRequest"
]

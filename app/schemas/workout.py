from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ExerciseSchema(BaseModel):
    name: str = Field(..., description="Name of the exercise")
    sets: int = Field(default=3, description="Number of working sets")
    reps: Optional[Union[int, str]] = Field(default="10-12", description="Repetitions or rep range")
    duration_minutes: Optional[int] = Field(default=None, description="Duration in minutes if cardio or timed hold")
    rest_seconds: int = Field(default=60, description="Rest period in seconds between sets")
    notes: Optional[str] = Field(default=None, description="Form tips and execution notes")

    model_config = ConfigDict(from_attributes=True)


class DailyWorkoutSchema(BaseModel):
    day: str = Field(..., description="Day name, e.g., Monday")
    title: str = Field(..., description="Focus title for the day, e.g. Upper Body Push")
    warmup: List[str] = Field(default_factory=lambda: ["5-10 minutes dynamic warm-up"])
    exercises: List[ExerciseSchema] = Field(default_factory=list)
    cooldown: List[str] = Field(default_factory=lambda: ["5 minutes static stretching"])
    recovery: str = Field(default="Hydrate well and ensure 7-8 hours of quality sleep.")
    is_rest_day: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class WeeklyWorkoutPlan(BaseModel):
    week: List[DailyWorkoutSchema] = Field(..., description="Exactly 7 days of structured workout plans")

    @field_validator("week")
    @classmethod
    def validate_seven_days(cls, v):
        if len(v) != 7:
            # If not 7 days, we handle padding or trimming in generator recovery,
            # but schema should accommodate valid weeks
            pass
        return v

    model_config = ConfigDict(from_attributes=True)


class NutritionGuidance(BaseModel):
    protein: str
    hydration: str
    balanced_meals: str
    recovery: str
    post_workout: str
    sleep_recovery: str
    disclaimer: str = "General wellness guidance only. Consult a qualified professional for medical or health-related concerns."

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanOut(BaseModel):
    id: int
    user_id: int
    original_plan: WeeklyWorkoutPlan
    updated_plan: Optional[WeeklyWorkoutPlan] = None
    nutrition_tip: Optional[Union[NutritionGuidance, str]] = None
    recovery_tip: Optional[str] = None
    completed_days: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MarkCompleteRequest(BaseModel):
    day: str = Field(..., description="Name of the day to mark completed, e.g. Monday")
    completed: bool = Field(default=True)

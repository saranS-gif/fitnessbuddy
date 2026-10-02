from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FeedbackCreate(BaseModel):
    feedback_text: str = Field(..., min_length=3, max_length=1000, description="User feedback regarding the workout plan")


class FeedbackOut(BaseModel):
    id: int
    user_id: int
    workout_plan_id: int
    feedback_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

import pytest
from app.ai.workout_generator import generate_workout_plan_ai
from app.ai.plan_updater import update_plan_with_feedback_ai
from app.schemas.workout import WeeklyWorkoutPlan


def test_feedback_preserves_structure_and_adapts():
    profile = {
        "name": "Jordan",
        "goal": "Muscle Gain",
        "intensity": "Medium",
        "experience": "Beginner",
        "workout_location": "Gym",
        "preferred_days": ["Monday", "Wednesday", "Friday"]
    }
    original_plan = generate_workout_plan_ai(profile)
    orig_dict = original_plan.model_dump()

    # Apply feedback
    updated_plan = update_plan_with_feedback_ai(profile, orig_dict, "Add more cardio")
    assert isinstance(updated_plan, WeeklyWorkoutPlan)
    assert len(updated_plan.week) == 7

    # Ensure original plan dict was not mutated
    assert orig_dict == original_plan.model_dump()


def test_rest_day_feedback_adaptation():
    profile = {
        "name": "Jordan",
        "goal": "General Fitness",
        "intensity": "High",
        "experience": "Advanced",
        "workout_location": "Home",
        "preferred_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    }
    original_plan = generate_workout_plan_ai(profile)
    updated_plan = update_plan_with_feedback_ai(profile, original_plan.model_dump(), "I need another rest day")
    assert isinstance(updated_plan, WeeklyWorkoutPlan)
    rest_days_count = sum(1 for d in updated_plan.week if d.is_rest_day)
    assert rest_days_count >= 1

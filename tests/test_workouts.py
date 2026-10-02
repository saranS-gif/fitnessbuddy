import pytest
from app.ai.workout_generator import generate_workout_plan_ai
from app.ai.nutrition_generator import generate_nutrition_plan_ai
from app.schemas.workout import WeeklyWorkoutPlan, NutritionGuidance


def test_workout_plan_has_seven_days():
    user_profile = {
        "name": "Jordan",
        "age": 25,
        "weight": 70.0,
        "goal": "Muscle Gain",
        "intensity": "High",
        "experience": "Intermediate",
        "workout_location": "Home",
        "preferred_days": ["Monday", "Tuesday", "Thursday", "Friday"]
    }
    plan = generate_workout_plan_ai(user_profile)
    assert isinstance(plan, WeeklyWorkoutPlan)
    assert len(plan.week) == 7

    day_names = [d.day for d in plan.week]
    assert day_names == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Verify each day has warmup, cooldown, recovery, exercises
    for day in plan.week:
        assert isinstance(day.warmup, list)
        assert isinstance(day.cooldown, list)
        assert isinstance(day.recovery, str)


def test_nutrition_guidance_generation():
    user_profile = {
        "name": "Jordan",
        "goal": "Weight Loss",
        "intensity": "Medium",
        "weight": 75.0
    }
    nutrition = generate_nutrition_plan_ai(user_profile)
    assert isinstance(nutrition, NutritionGuidance)
    assert nutrition.protein is not None
    assert nutrition.hydration is not None
    assert nutrition.balanced_meals is not None
    assert "General wellness guidance only" in nutrition.disclaimer

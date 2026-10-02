import copy
import json
import logging
import re
from typing import Dict, Any
from app.ai.gemini_client import get_gemini_client
from app.schemas.workout import WeeklyWorkoutPlan, DailyWorkoutSchema, ExerciseSchema

logger = logging.getLogger("fitbuddy.ai")


def update_plan_with_feedback_ai(
    user_profile: Dict[str, Any],
    original_plan_dict: Dict[str, Any],
    feedback_text: str
) -> WeeklyWorkoutPlan:
    """
    Synthesize user profile, the existing workout plan, and specific user feedback
    through Gemini AI to generate an updated 7-day workout plan.
    The original plan structure remains intact; an updated plan is returned.
    """
    model = get_gemini_client()
    clean_feedback = feedback_text.strip()

    if model:
        prompt = f"""
You are FitBuddy's adaptive AI fitness coach.
A user has submitted specific feedback regarding their current 7-day workout regimen.

USER PROFILE:
- Name: {user_profile.get('name', 'Athlete')}
- Goal: {user_profile.get('goal')}
- Intensity: {user_profile.get('intensity')}
- Experience: {user_profile.get('experience')}
- Location: {user_profile.get('workout_location')}

USER FEEDBACK:
"{clean_feedback}"

CURRENT WORKOUT PLAN (JSON):
{json.dumps(original_plan_dict, indent=2)}

TASK:
Generate an UPDATED 7-day workout plan that directly addresses the user's feedback.
- If the user asked for "more cardio", integrate cardio sessions, intervals, or conditioning blocks.
- If the user asked to "make workouts easier" or "reduce intensity", reduce working sets, increase rest periods, or swap in lighter variations.
- If the user requested "another rest day", convert the most taxing workout day into an Active Recovery / Rest day.
- If the user asked for "home workouts", convert gym movements to bodyweight/minimal equipment movements.
- If the user requested "reduce leg exercises", replace strenuous lower-body compound lifts with upper-body, core, or low-impact mobility.
- If the user asked for "make workouts shorter", streamline exercise count and superset/reduce rest.

MANDATORY RULES:
1. Output MUST be strictly valid JSON matching the exact WeeklyWorkoutPlan schema:
{{
  "week": [
    {{
      "day": "Monday",
      "title": "Updated Title",
      "warmup": ["Warm-up step"],
      "exercises": [
        {{
          "name": "Exercise Name",
          "sets": 3,
          "reps": "10-12",
          "duration_minutes": null,
          "rest_seconds": 60,
          "notes": "Execution note reflecting feedback"
        }}
      ],
      "cooldown": ["Cooldown step"],
      "recovery": "Recovery tip",
      "is_rest_day": false
    }}
  ]
}}
2. Output EXACTLY 7 items in the "week" array covering Monday through Sunday.
3. Return pure raw JSON without markdown formatting.
"""
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
                request_options={"timeout": 15}
            )
            raw = response.text.strip()
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"^```\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

            parsed = json.loads(raw)
            if "week" in parsed and len(parsed["week"]) == 7:
                return WeeklyWorkoutPlan(**parsed)
        except Exception as e:
            logger.error(f"Gemini plan update failed ({e}). Applying intelligent heuristic adaptation.")

    # Rule-based adaptation engine
    return _apply_heuristic_feedback_update(original_plan_dict, clean_feedback)


def _apply_heuristic_feedback_update(
    original_plan_dict: Dict[str, Any],
    feedback: str
) -> WeeklyWorkoutPlan:
    """Adapts an existing plan based on feedback keywords if AI is offline."""
    updated = copy.deepcopy(original_plan_dict)
    week_days = updated.get("week", [])
    fb_lower = feedback.lower()

    for idx, day in enumerate(week_days):
        exercises = day.get("exercises", [])

        # 1. More cardio
        if "cardio" in fb_lower:
            if not day.get("is_rest_day"):
                exercises.append({
                    "name": "HIIT Incline Treadmill or Jump Rope Finisher",
                    "sets": 1,
                    "reps": "10 rounds (30s on / 30s off)",
                    "duration_minutes": 10,
                    "rest_seconds": 30,
                    "notes": "Added per feedback: Elevate aerobic conditioning"
                })

        # 2. Make easier / reduce intensity
        elif "easier" in fb_lower or "less intense" in fb_lower or "reduce intensity" in fb_lower:
            for ex in exercises:
                if ex.get("sets", 3) > 2:
                    ex["sets"] -= 1
                ex["rest_seconds"] = ex.get("rest_seconds", 60) + 30
                ex["notes"] = (ex.get("notes") or "") + " (Adjusted for recovery: reduced volume)"

        # 3. Another rest day
        elif "rest" in fb_lower or "rest day" in fb_lower:
            if idx == 3 and not day.get("is_rest_day"):  # Convert Thursday / Day 4
                day["title"] = "Additional Active Recovery (Per Feedback)"
                day["is_rest_day"] = True
                day["exercises"] = [{
                    "name": "Gentle 30-min Nature Walk & Mobility Flow",
                    "sets": 1,
                    "reps": "1 session",
                    "duration_minutes": 30,
                    "rest_seconds": 0,
                    "notes": "Dedicated passive restoration day added"
                }]

        # 4. Home workouts
        elif "home" in fb_lower:
            for ex in exercises:
                name = ex.get("name", "")
                if "barbell" in name.lower() or "cable" in name.lower() or "machine" in name.lower():
                    ex["name"] = name.replace("Barbell", "Bodyweight / Banded").replace("Cable", "Towel / Resistance Band")
                    ex["notes"] = (ex.get("notes") or "") + " [Adapted for Home Setup]"

        # 5. Reduce legs
        elif "leg" in fb_lower or "legs" in fb_lower:
            day["exercises"] = [
                ex for ex in exercises if not any(leg_word in ex.get("name", "").lower() for leg_word in ["squat", "deadlift", "lunge", "calf", "leg"] )
            ]
            if len(day["exercises"]) == 0 and not day.get("is_rest_day"):
                day["exercises"] = [{
                    "name": "Plank & Core Hollow Hold",
                    "sets": 3,
                    "reps": "45s",
                    "duration_minutes": 1,
                    "rest_seconds": 45,
                    "notes": "Low-impact core stability substitution"
                }]

        # 6. Shorter sessions
        elif "shorter" in fb_lower or "quick" in fb_lower:
            if len(exercises) > 3:
                day["exercises"] = exercises[:3]
                day["title"] = day.get("title", "") + " (Express 30m)"

    return WeeklyWorkoutPlan(**updated)

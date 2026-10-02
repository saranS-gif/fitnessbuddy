import json
import logging
import re
from typing import Dict, Any, Optional
from app.config import settings
from app.ai.workout_generator import generate_fallback_plan, DAYS_OF_WEEK

logger = logging.getLogger("fitbuddy")


def get_gemini_model() -> Optional[Any]:
    api_key = (settings.GEMINI_API_KEY or "").strip()
    if not api_key or api_key in ("", "your_api_key_here", "your_gemini_api_key_here"):
        print("[FitBuddy] Gemini API key not configured. Running FitBuddy in fallback mode.")
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL or "gemini-1.5-flash")
        print("[FitBuddy] Gemini configured")
        return model
    except Exception as e:
        print(f"[FitBuddy] Warning: Could not initialize Gemini model ({e}). Will use fallback.")
        return None


def _clean_and_parse_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return None


def generate_workout_plan(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    print("[FitBuddy] Workout generation started")
    model = get_gemini_model()

    if model:
        name = user_profile.get("name", "Athlete")
        age = user_profile.get("age", 25)
        weight = user_profile.get("weight", 70)
        height = user_profile.get("height", 170)
        goal = user_profile.get("goal", "General Fitness")
        intensity = user_profile.get("intensity", "Medium")
        experience = user_profile.get("experience", "Beginner")
        location = user_profile.get("location", "Home")
        equipment = user_profile.get("equipment", "None")
        preferred_days = user_profile.get("preferred_days", ["Monday", "Wednesday", "Friday"])
        days_str = ", ".join(preferred_days)

        prompt = f"""
You are FitBuddy's master exercise physiologist and AI coach.
Create an elite, science-backed 7-day workout routine tailored precisely to:
- Athlete: {name} (Age: {age}, Weight: {weight} kg, Height: {height} cm)
- Primary Goal: {goal}
- Intensity Level: {intensity}
- Experience: {experience}
- Workout Location: {location}
- Available Equipment: {equipment}
- Preferred Training Days: {days_str}

MANDATORY RULES:
1. Return ONLY pure valid JSON matching this schema:
{{
  "summary": "High-level summary of the training week and progressive strategy",
  "weekly_goal": "Specific physiological focus for this week",
  "days": [
    {{
      "day": "Monday",
      "focus": "Workout Focus or Active Recovery",
      "type": "Workout",
      "warmup": ["Warm-up movement 1", "Warm-up movement 2"],
      "exercises": [
        {{
          "name": "Exercise Name",
          "sets": 3,
          "reps": "10-12",
          "rest_seconds": 60,
          "instructions": "Form cues and execution details"
        }}
      ],
      "cooldown": ["Cool-down stretch 1", "Cool-down stretch 2"],
      "recovery": "Daily recovery guidance"
    }}
  ],
  "nutrition": {{
    "calories_guidance": "Recommended daily caloric target or surplus/deficit guidelines",
    "protein_guidance": "Specific daily protein target in grams and quality food sources",
    "hydration": "Daily water intake target in Liters",
    "tip": "Targeted nutrition and meal-timing strategy"
  }},
  "disclaimer": "General wellness guidance only. Consult a qualified professional for medical concerns."
}}
2. The "days" array MUST contain EXACTLY 7 items in order: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.
3. Days not in preferred days ({days_str}) MUST have "type": "Rest", focus: "Active Recovery & Mobility", and gentle mobility/walking exercises.
4. If location is Home or equipment is None/Dumbbells, only specify suitable movements.
5. Do NOT output markdown code blocks (```json), commentary, or extra text. Output ONLY pure raw JSON.
"""
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            parsed = _clean_and_parse_json(response.text)
            if parsed and isinstance(parsed, dict) and "days" in parsed and len(parsed["days"]) == 7:
                parsed["is_fallback"] = False
                print("[FitBuddy] Gemini response received")
                return parsed
            else:
                print("[FitBuddy] Gemini returned incomplete structure. Employing safe fallback engine.")
        except Exception as e:
            print(f"[FitBuddy] Gemini call failed ({e}). Employing fallback engine.")

    plan = generate_fallback_plan(user_profile)
    return plan


def generate_updated_plan(
    user_profile: Dict[str, Any],
    original_plan: Dict[str, Any],
    feedback_text: str
) -> Dict[str, Any]:
    print("[FitBuddy] Feedback update generation started")
    model = get_gemini_model()

    if model:
        prompt = f"""
You are FitBuddy's master exercise physiologist.
The user provided feedback to adjust their current 7-day workout plan.

USER PROFILE:
- Name: {user_profile.get('name', 'Athlete')}
- Goal: {user_profile.get('goal')}
- Intensity: {user_profile.get('intensity')}
- Experience: {user_profile.get('experience')}
- Location: {user_profile.get('location')}
- Equipment: {user_profile.get('equipment')}

CURRENT PLAN (JSON):
{json.dumps(original_plan, indent=2)}

USER FEEDBACK:
"{feedback_text}"

TASK:
Produce an UPDATED 7-day plan that directly incorporates the user's feedback.
- Maintain the exact same JSON schema with 7 days (Monday through Sunday), summary, weekly_goal, nutrition, disclaimer.
- Output ONLY pure JSON.
"""
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            parsed = _clean_and_parse_json(response.text)
            if parsed and isinstance(parsed, dict) and "days" in parsed and len(parsed["days"]) == 7:
                parsed["is_fallback"] = False
                print("[FitBuddy] Updated Gemini response received")
                return parsed
        except Exception as e:
            print(f"[FitBuddy] Gemini update failed ({e}). Applying safe rule adjustments.")

    import copy
    updated = copy.deepcopy(original_plan)
    fb_lower = feedback_text.lower()
    updated["summary"] = f"{updated.get('summary', '')} [Updated: {feedback_text}]"

    for day in updated.get("days", []):
        if "easier" in fb_lower or "less intensity" in fb_lower:
            for ex in day.get("exercises", []):
                if isinstance(ex.get("sets"), int) and ex["sets"] > 2:
                    ex["sets"] -= 1
                ex["rest_seconds"] = ex.get("rest_seconds", 60) + 15
        elif "more cardio" in fb_lower:
            if day.get("type") == "Workout":
                day["exercises"].append({
                    "name": "15-Minute HIIT / Cardio Finisher",
                    "sets": 1,
                    "reps": "15 mins",
                    "rest_seconds": 30,
                    "instructions": "Moderate-to-high intensity aerobic intervals."
                })
        elif "rest" in fb_lower and "more" in fb_lower:
            if day.get("day") in ["Wednesday", "Sunday"]:
                day["type"] = "Rest"
                day["focus"] = "Active Recovery & Mobility"
        elif "shorter" in fb_lower:
            if len(day.get("exercises", [])) > 3:
                day["exercises"] = day["exercises"][:3]

    updated["is_fallback"] = True
    return updated

import json
import logging
import re
from typing import Dict, Any
from app.ai.gemini_client import get_gemini_client
from app.schemas.workout import NutritionGuidance

logger = logging.getLogger("fitbuddy.ai")

DISCLAIMER_TEXT = "General wellness guidance only. Consult a qualified professional for medical or health-related concerns."


def generate_nutrition_plan_ai(user_profile: Dict[str, Any]) -> NutritionGuidance:
    model = get_gemini_client()
    goal = user_profile.get("goal", "General Fitness")
    intensity = user_profile.get("intensity", "Medium")
    weight = user_profile.get("weight", 70.0)
    name = user_profile.get("name", "Athlete")

    if model:
        prompt = f"""
You are an expert sports performance nutritionist.
Create concise, evidence-based nutrition and recovery guidance for {name}:
- Goal: {goal}
- Workout Intensity: {intensity}
- Body Weight: {weight} kg

Return ONLY valid JSON matching this schema:
{{
  "protein": "Specific daily protein recommendation (e.g. 1.6-2.0g per kg of bodyweight) with quality food sources.",
  "hydration": "Daily fluid intake target in liters/ounces with electrolytes guidance for {intensity} workouts.",
  "balanced_meals": "Macronutrient plate composition balance for {goal}.",
  "recovery": "Active recovery, joint support, and rest day dietary strategies.",
  "post_workout": "Optimal timing and nutrient ratio within 45-90 minutes post-training.",
  "sleep_recovery": "Sleep hygiene and physiological regeneration advice."
}}
Do NOT include markdown backticks or commentary outside JSON.
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
            parsed["disclaimer"] = DISCLAIMER_TEXT
            return NutritionGuidance(**parsed)
        except Exception as e:
            logger.error(f"Gemini nutrition generation failed ({e}). Using intelligent rule engine.")

    return _build_fallback_nutrition(goal, intensity, weight)


def _build_fallback_nutrition(goal: str, intensity: str, weight: float) -> NutritionGuidance:
    weight = float(weight) if weight else 70.0
    is_muscle = "muscle" in goal.lower()
    is_fat_loss = "loss" in goal.lower() or "weight" in goal.lower()

    if is_muscle:
        protein_target = f"{int(weight * 1.8)}-{int(weight * 2.2)}g/day (~{round(weight * 2.0, 1)}g average)"
        meals = "Slight caloric surplus (+250-400 kcal): 45% complex carbs, 30% lean protein, 25% healthy fats."
        post_wo = "30-40g fast-digesting protein paired with 40-60g simple/moderate carbs (e.g. whey shake + banana)."
    elif is_fat_loss:
        protein_target = f"{int(weight * 1.8)}-{int(weight * 2.0)}g/day to preserve lean muscle during a caloric deficit."
        meals = "Moderate caloric deficit (-300-500 kcal): high vegetable volume, 35% lean protein, 35% fiber-rich carbs, 30% healthy fats."
        post_wo = "25-30g lean protein with leafy greens and moderate carbs within 60 minutes."
    else:
        protein_target = f"{int(weight * 1.4)}-{int(weight * 1.6)}g/day for cellular repair and metabolic health."
        meals = "Caloric maintenance with balanced micronutrient distribution across whole grains, lean poultry/tofu, and fruits."
        post_wo = "Balanced meal containing 20-30g protein and complex carbohydrates within 90 minutes."

    water_target = round(weight * 0.04 + (0.5 if intensity == "High" else 0.2), 1)

    return NutritionGuidance(
        protein=f"Aim for {protein_target}. Excellent sources include eggs, chicken breast, Greek yogurt, salmon, lentils, and tempeh.",
        hydration=f"Consume at least {water_target} Liters of water daily. For {intensity.lower()}-intensity days, consider adding a pinch of sea salt or electrolytes.",
        balanced_meals=meals,
        recovery="Focus on anti-inflammatory whole foods (berries, dark leafy greens, omega-3 rich fish or chia seeds) to accelerate tissue regeneration.",
        post_workout=post_wo,
        sleep_recovery="Prioritize 7.5 to 8.5 hours of uninterrupted sleep in a cool, dark environment to facilitate growth hormone release.",
        disclaimer=DISCLAIMER_TEXT
    )

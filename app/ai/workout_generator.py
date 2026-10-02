import logging
from typing import Dict, Any, List

logger = logging.getLogger("fitbuddy")

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def generate_fallback_plan(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligent, deterministic rule-based fallback generator.
    Creates a complete 7-day workout plan and nutrition guidance adhering strictly to the schema.
    Used when Gemini API key is missing, network is down, or Gemini fails.
    """
    name = user_profile.get("name", "Athlete")
    goal = user_profile.get("goal", "General Fitness")
    intensity = user_profile.get("intensity", "Medium")
    experience = user_profile.get("experience", "Beginner")
    location = user_profile.get("location", "Home")
    equipment = user_profile.get("equipment", "None")
    preferred_days = user_profile.get("preferred_days", ["Monday", "Wednesday", "Friday"])
    weight = float(user_profile.get("weight", 70.0))
    height = float(user_profile.get("height", 170.0))

    is_home = location.lower() == "home"
    is_outdoor = location.lower() == "outdoor"
    is_gym = location.lower() == "gym" or "gym" in equipment.lower()

    # Predefined safe, progressive workout splits
    split_templates = [
        {
            "focus": "Upper Body Strength & Posture",
            "warmup": [
                "3 minutes dynamic arm circles & wrist mobility",
                "2 minutes jumping jacks or high knees",
                "10 reps inchworms with shoulder taps"
            ],
            "exercises": [
                {
                    "name": "Standard Push-Ups" if (is_home or is_outdoor) else "Barbell / Dumbbell Bench Press",
                    "sets": 3,
                    "reps": "10-12" if experience != "Beginner" else "8-10",
                    "rest_seconds": 60,
                    "instructions": "Keep core engaged, elbows at 45 degrees, and lower chest smoothly."
                },
                {
                    "name": "Doorframe / Inverted Rows" if (is_home or is_outdoor) else "Lat Pulldown or Seated Cable Row",
                    "sets": 3,
                    "reps": "10-12",
                    "rest_seconds": 60,
                    "instructions": "Retract scapulae and pull with elbows, feeling the mid-back engage."
                },
                {
                    "name": "Pike Push-Ups" if is_home else "Dumbbell Overhead Shoulder Press",
                    "sets": 3,
                    "reps": "10",
                    "rest_seconds": 60,
                    "instructions": "Press overhead without arching the lower back; brace your abdominal wall."
                },
                {
                    "name": "Chair / Bench Triceps Dips",
                    "sets": 3,
                    "reps": "12",
                    "rest_seconds": 45,
                    "instructions": "Lower until upper arms are parallel to ground, keep chest upright."
                }
            ],
            "cooldown": [
                "Standing doorway chest stretch (30s each side)",
                "Cross-body shoulder stretch (30s each side)",
                "Child's pose lat stretch (45s)"
            ],
            "recovery": "Rehydrate with water and consume 25-30g of protein within 90 minutes."
        },
        {
            "focus": "Lower Body Power & Core Foundation",
            "warmup": [
                "3 minutes bodyweight air squats & hip openers",
                "2 minutes walking lunges with torso twists",
                "15 reps glute bridges"
            ],
            "exercises": [
                {
                    "name": "Tempo Bodyweight Squats" if is_home else "Goblet Squats or Barbell Back Squats",
                    "sets": 3,
                    "reps": "12-15",
                    "rest_seconds": 75,
                    "instructions": "Keep knees tracking over toes, chest tall, 3 seconds lowering down."
                },
                {
                    "name": "Alternating Walking Lunges",
                    "sets": 3,
                    "reps": "10 per leg",
                    "rest_seconds": 60,
                    "instructions": "Step forward smoothly, dropping back knee gently toward the floor."
                },
                {
                    "name": "Single-Leg Glute Bridges",
                    "sets": 3,
                    "reps": "12 per side",
                    "rest_seconds": 45,
                    "instructions": "Drive through the heel and squeeze glute at the top for 1 full second."
                },
                {
                    "name": "Deadbugs / Forearm Plank",
                    "sets": 3,
                    "reps": "45s hold",
                    "rest_seconds": 45,
                    "instructions": "Maintain flat lower back contact and prevent pelvis from dipping."
                }
            ],
            "cooldown": [
                "Standing quad stretch (30s per leg)",
                "Seated hamstring stretch (30s per leg)",
                "Figure-four glute stretch (30s per leg)"
            ],
            "recovery": "Perform light leg elevation or a warm shower to promote lymphatic drainage."
        },
        {
            "focus": "Full Body Metabolic Conditioning",
            "warmup": [
                "3 minutes light jog in place with arm swings",
                "2 minutes butt kicks and torso rotations",
                "10 reps unweighted good mornings"
            ],
            "exercises": [
                {
                    "name": "Mountain Climbers",
                    "sets": 3,
                    "reps": "30s work",
                    "rest_seconds": 45,
                    "instructions": "Drive knees alternately toward chest keeping hips level with shoulders."
                },
                {
                    "name": "Jump Rope or Simulated Jump Rope",
                    "sets": 3,
                    "reps": "45s steady",
                    "rest_seconds": 45,
                    "instructions": "Stay light on the balls of your feet with rhythm."
                },
                {
                    "name": "Step-Ups (Chair, Step, or Bench)",
                    "sets": 3,
                    "reps": "12 per leg",
                    "rest_seconds": 60,
                    "instructions": "Plant whole foot on step, drive through heel, stand tall."
                },
                {
                    "name": "Bicycle Crunches",
                    "sets": 3,
                    "reps": "20 total",
                    "rest_seconds": 45,
                    "instructions": "Slow, controlled rotation connecting opposite elbow toward knee."
                }
            ],
            "cooldown": [
                "Downward-facing dog calf stretch (45s)",
                "Cobra abdominal stretch (30s)",
                "Deep diaphragmatic box breathing (2 minutes)"
            ],
            "recovery": "Replenish sodium/electrolytes if sweating heavily; sleep at least 7.5 hours."
        }
    ]

    # Build 7-day schedule
    days_list = []
    training_day_index = 0

    for day_name in DAYS_OF_WEEK:
        is_training = any(d.lower() == day_name.lower() for d in preferred_days)
        if is_training:
            template = split_templates[training_day_index % len(split_templates)]
            training_day_index += 1
            days_list.append({
                "day": day_name,
                "focus": f"{template['focus']} ({intensity})",
                "type": "Workout",
                "warmup": template["warmup"],
                "exercises": template["exercises"],
                "cooldown": template["cooldown"],
                "recovery": template["recovery"]
            })
        else:
            days_list.append({
                "day": day_name,
                "focus": "Active Recovery & Mobility",
                "type": "Rest",
                "warmup": ["5 minutes gentle neck, shoulder, and hip mobility circles"],
                "exercises": [
                    {
                        "name": "Low-Intensity Recovery Walk",
                        "sets": 1,
                        "reps": "20-30 mins",
                        "rest_seconds": 0,
                        "instructions": "Maintain comfortable nasal breathing to promote active blood circulation."
                    },
                    {
                        "name": "Full Body Mobility & Foam Rolling",
                        "sets": 2,
                        "reps": "45s per area",
                        "rest_seconds": 30,
                        "instructions": "Target tight calves, quads, and thoracic spine with deep breathing."
                    }
                ],
                "cooldown": ["5 minutes supine diaphragmatic relaxation"],
                "recovery": "Prioritize high-quality sleep, nutrient-dense whole foods, and hydration."
            })

    # Nutrition targets based on user biometric attributes
    is_muscle = "muscle" in goal.lower() or "strength" in goal.lower()
    is_loss = "loss" in goal.lower() or "weight" in goal.lower()

    if is_muscle:
        cals = f"Slight surplus (+250 to +350 kcal above maintenance, ~{int(weight * 33 + 300)} kcal/day)."
        protein = f"Aim for {int(weight * 1.8)}g – {int(weight * 2.2)}g protein daily (~2.0g/kg) from lean meats, eggs, tofu, fish, or whey."
    elif is_loss:
        cals = f"Moderate deficit (-300 to -500 kcal below maintenance, ~{int(weight * 28 - 300)} kcal/day)."
        protein = f"Aim for {int(weight * 1.8)}g – {int(weight * 2.0)}g protein daily to preserve lean muscle mass during fat loss."
    else:
        cals = f"Caloric balance at maintenance (~{int(weight * 31)} kcal/day) with nutrient-dense whole foods."
        protein = f"Aim for {int(weight * 1.4)}g – {int(weight * 1.6)}g protein daily (~{int(weight * 1.5)}g average)."

    water_liters = round(weight * 0.038 + (0.5 if intensity == "High" else 0.2), 1)

    return {
        "summary": f"Personalized 7-day {goal.lower()} program tailored for {name} ({intensity} intensity, {location} training with {equipment}).",
        "weekly_goal": f"Execute scheduled workouts with progressive consistency and prioritize recovery on off-days.",
        "days": days_list,
        "nutrition": {
            "calories_guidance": cals,
            "protein_guidance": protein,
            "hydration": f"Drink at least {water_liters} Liters of water daily, adding electrolytes on high-exertion days.",
            "tip": f"Eat balanced whole-food meals emphasizing colorful vegetables, complex carbs, and healthy fats."
        },
        "disclaimer": "General wellness guidance only. Consult a qualified professional for medical concerns.",
        "is_fallback": True
    }

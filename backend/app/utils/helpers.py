from typing import Dict


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation."""
    if gender and gender.lower() == "female":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5


def calculate_tdee(bmr: float, days_per_week: int) -> float:
    """Calculate Total Daily Energy Expenditure based on training frequency."""
    multipliers = {
        0: 1.2,     # Sedentary
        1: 1.375,   # Light
        2: 1.375,
        3: 1.55,    # Moderate
        4: 1.55,
        5: 1.725,   # Heavy
        6: 1.725,
        7: 1.9      # Extreme
    }
    multiplier = multipliers.get(min(max(days_per_week, 0), 7), 1.45)
    return bmr * multiplier


def calculate_macros(tdee: float, goal: str) -> Dict[str, int]:
    """Calculate recommended target calories and macronutrients."""
    if goal == "fat_loss":
        target_calories = int(tdee * 0.8)
        protein_ratio, fat_ratio, carb_ratio = 0.35, 0.25, 0.40
    elif goal == "muscle_gain":
        target_calories = int(tdee * 1.15)
        protein_ratio, fat_ratio, carb_ratio = 0.30, 0.25, 0.45
    else:
        target_calories = int(tdee)
        protein_ratio, fat_ratio, carb_ratio = 0.25, 0.25, 0.50

    protein_grams = int((target_calories * protein_ratio) / 4)
    fats_grams = int((target_calories * fat_ratio) / 9)
    carbs_grams = int((target_calories * carb_ratio) / 4)

    return {
        "calories": target_calories,
        "protein_grams": protein_grams,
        "fats_grams": fats_grams,
        "carbs_grams": carbs_grams
    }

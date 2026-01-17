from typing import Optional
from dataclasses import dataclass

import re
from googletrans import Translator

from api.fatsecret import FatSecretClient

from config import (
    FATSECRET_CLIENT_ID,
    FATSECRET_CLIENT_SECRET,
    FATSECRET_SAVE_PATH
)


@dataclass
class NutritionInfo:
    calories: float
    fat: float
    carbs: float
    protein: float


class FoodManager:
    
    def __init__(self) -> None:
        self.fatsecret_client = FatSecretClient(
            client_id=FATSECRET_CLIENT_ID,
            client_secret=FATSECRET_CLIENT_SECRET,
            save_path=FATSECRET_SAVE_PATH
        )
        self.translator = Translator()

    @staticmethod
    def parse_food_description(description: str) -> Optional[NutritionInfo]:
        try:
            calories_match = re.search(r'Calories:\s*([\d.]+)', description)
            calories = float(calories_match.group(1)) if calories_match else 0.0
            fat_match = re.search(r'Fat:\s*([\d.]+)', description)
            fat = float(fat_match.group(1)) if fat_match else 0.0
            carbs_match = re.search(r'Carbs:\s*([\d.]+)', description)
            carbs = float(carbs_match.group(1)) if carbs_match else 0.0
            protein_match = re.search(r'Protein:\s*([\d.]+)', description)
            protein = float(protein_match.group(1)) if protein_match else 0.0
            return NutritionInfo(
                calories=calories,
                fat=fat,
                carbs=carbs,
                protein=protein
            )
        except Exception as e:
            print(f"Error parsing food description: {e}")
            return None

    async def get_calories_per_100g(
        self,
        food_name: str
    ) -> float | None:
        translated_name = await self.translate_food_name(food_name)
        if not translated_name:
            return None
        food_data = await self.fatsecret_client.get_food_data(translated_name, max_results=1)
        if not food_data:
            return None
        nutrition_info = self.parse_food_description(food_data[0].food_description)
        if nutrition_info:
            return nutrition_info.calories
        return None
    
    async def translate_food_name(
        self,
        food_name: str
    ) -> str | None:
        try:
            result = await self.translator.translate(
                food_name,            
                dest='en'
            )
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return None
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Union, List


class TokenData(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Food(BaseModel):
    food_id: str
    food_name: str
    food_type: str
    food_description: str
    food_url: str


class FoodData(BaseModel):
    food: Union[Food, List[Food]]
    max_results: str
    page_number: str
    total_results: str


class FoodSearchResponse(BaseModel):
    foods: FoodData
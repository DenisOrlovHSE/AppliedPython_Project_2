from pydantic import BaseModel
from datetime import date


class HealthProfileDTO(BaseModel):
    weight: float
    height: int
    age: int
    activity: str
    city: str
    calorie_goal: int


class DailyProgressDTO(BaseModel):
    day: str
    water_goal: int
    water_consumed: int
    calories_goal: int
    calories_consumed: int
    calories_burned: int


class CalorieHistoryDTO(BaseModel):
    date_info: date
    calories_consumed: int
    calories_burned: int


class WaterHistoryDTO(BaseModel):
    date_info: date
    water_consumed: int
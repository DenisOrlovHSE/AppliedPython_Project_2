from typing import Optional

from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from database.repository import Repository
from database.models import (
    DailyCaloriesStats,
    DailyWaterStats
)
from application.dto import (
    HealthProfileDTO,
    DailyProgressDTO,
    CalorieHistoryDTO,
    WaterHistoryDTO
)
from api.owm import OWMClient

from config import OWM_API_KEY

from .food_manager import FoodManager
from .workout_manager import WorkoutManager


class Service:

    def __init__(
        self,
        db_session: AsyncSession
    ) -> None:
        self.db_session = db_session
        self.food_manager = FoodManager()
        self.workout_manager = WorkoutManager()

    async def create_user(
        self,
        telegram_id: int
    ) -> bool:
        repo = Repository(self.db_session)
        user = await repo.get_user_by_telegram_id(telegram_id)
        if not user:
            return await repo.add_user(telegram_id)
        return True

    async def update_health_profile(
        self,
        telegram_id: int,
        weight: float,
        height: float,
        age: int,
        activity: int,
        city: str,
        calorie_goal: Optional[int] = None,
    ) -> bool:
        repo = Repository(self.db_session)
        user = await repo.get_user_by_telegram_id(telegram_id)
        if not calorie_goal:
            calorie_goal = self.calculate_default_calorie_goal(
                weight=weight,
                height=height,
                age=age,
                activity=activity
            )
        if user:
            print("Updating health profile...")
            return await repo.update_health_profile(
                user_id=user.id,
                weight=weight,
                height=height,
                age=age,
                activity=activity,
                city=city,
                calorie_goal=calorie_goal
            )
        return False
    
    async def get_health_profile(
        self,
        telegram_id: int
    ) -> HealthProfileDTO | None:
        repo = Repository(self.db_session)
        user = await repo.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        profile_db = await repo.get_health_profile(user.id)
        if not profile_db:
            return None
        profile_dto = HealthProfileDTO(
            weight=profile_db.weight,
            height=profile_db.height,
            age=profile_db.age,
            activity=str(profile_db.activity),
            city=profile_db.city,
            calorie_goal=profile_db.calorie_goal
        )
        return profile_dto
    
    async def get_daily_progress(
        self,
        telegram_id: int
    ) -> DailyProgressDTO | None:
        repo = Repository(self.db_session)
        user = await repo.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        water_stats = await self.get_daily_water_stats(user.id, repo)
        calories_stats = await self.get_daily_calories_stats(user.id, repo)
        if not water_stats or not calories_stats:
            return None
        progress_dto = DailyProgressDTO(
            day=str(water_stats.day),
            water_goal=water_stats.water_goal,
            water_consumed=water_stats.water_consumed,
            calories_goal=calories_stats.calories_goal,
            calories_consumed=calories_stats.calories_consumed,
            calories_burned=calories_stats.calories_burned
        )
        return progress_dto
    
    def calculate_default_calorie_goal(
        self,
        weight: float,
        height: float,
        age: int,
        activity: int
    ) -> int:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
        if activity < 30:
            multiplier = 1.2
        elif activity < 60:
            multiplier = 1.375
        elif activity < 120:
            multiplier = 1.55
        elif activity < 180:
            multiplier = 1.725
        else:
            multiplier = 1.9
        return int(bmr * multiplier)
    
    async def get_daily_water_stats(
        self,
        user_id: int,
        repo: Repository
    ) -> Optional[DailyWaterStats]:
        current_date = date.today()
        water_stats = await repo.get_daily_water_stat(user_id, current_date)
        if water_stats is not None:
            return water_stats
        profile = await repo.get_health_profile(user_id)
        if profile is None:
            return None
        water_goal = await self._calculate_default_water_goal(profile.weight, profile.activity, profile.city)
        water_stats = await repo.update_daily_water_stats(
            user_id=user_id,
            day=current_date,
            water_goal=water_goal
        )
        return water_stats
    
    async def get_daily_calories_stats(
        self,
        user_id: int,
        repo: Repository
    ) -> Optional[DailyCaloriesStats]:
        current_date = date.today()
        calories_stats = await repo.get_daily_calories_stat(user_id, current_date)
        if calories_stats is not None:
            return calories_stats
        profile = await repo.get_health_profile(user_id)
        if profile is None:
            return None
        calories_goal = profile.calorie_goal
        calories_stats = await repo.update_daily_calories_stats(
            user_id=user_id,
            day=current_date,
            calories_goal=calories_goal
        )
        return calories_stats
    
    async def log_water_consumption(
        self,
        telegram_id: int,
        amount: int
    ) -> bool:
        repo = Repository(self.db_session)
        user = await repo.get_user_by_telegram_id(telegram_id)
        if not user:
            return False
        current_date = date.today()
        water_stats = await self.get_daily_water_stats(user.id, repo)
        if not water_stats:
            return False
        new_amount = water_stats.water_consumed + amount
        await repo.update_daily_water_stats(
            user_id=user.id,
            day=current_date,
            water_goal=water_stats.water_goal,
            water_consumed=new_amount
        )
        return True
    
    async def get_food_calories_per_100g(
        self,
        food_name: str
    ) -> float:
        result = await self.food_manager.get_calories_per_100g(food_name)
        return result if result is not None else 0.0
    
    async def log_food_consumption(
        self,
        telegram_id: int,
        calories_per_100g: float,
        amount_in_grams: float
    ) -> tuple[bool, float]:
        repo = Repository(self.db_session)
        user = await repo.get_user_by_telegram_id(telegram_id)
        if not user:
            return False, 0.0
        total_calories = (calories_per_100g * amount_in_grams) / 100
        current_date = date.today()
        calories_stats = await self.get_daily_calories_stats(user.id, repo)
        if not calories_stats:
            return False, 0.0
        new_calories_consumed = calories_stats.calories_consumed + int(total_calories)
        await repo.update_daily_calories_stats(
            user_id=user.id,
            day=current_date,
            calories_goal=calories_stats.calories_goal,
            calories_consumed=new_calories_consumed,
            calories_burned=calories_stats.calories_burned
        )
        return True, total_calories
    
    async def log_workout(
        self,
        telegram_id: int,
        exercise_name: str,
        duration_minutes: float
    ) -> tuple[bool, float, float]:
        burned_calories = self.workout_manager.get_burned_calories(
            exercise_name=exercise_name,
            duration_minutes=duration_minutes
        )
        additonal_water_goal = duration_minutes // 30 * 200
        repo = Repository(self.db_session)
        user = await repo.get_user_by_telegram_id(telegram_id)
        if not user:
            return False, 0.0, 0.0
        current_date = date.today()
        water_stats = await self.get_daily_water_stats(user.id, repo)
        if not water_stats:
            return False, 0.0, 0.0
        new_water_goal = water_stats.water_goal + additonal_water_goal
        await repo.update_daily_water_stats(
            user_id=user.id,
            day=current_date,
            water_goal=new_water_goal,
            water_consumed=water_stats.water_consumed
        )
        calories_stats = await self.get_daily_calories_stats(user.id, repo)
        if not calories_stats:
            return False, 0.0, 0.0
        new_calories_burned = calories_stats.calories_burned + int(burned_calories)
        await repo.update_daily_calories_stats(
            user_id=user.id,
            day=current_date,
            calories_goal=calories_stats.calories_goal,
            calories_consumed=calories_stats.calories_consumed,
            calories_burned=new_calories_burned
        )
        return True, burned_calories, additonal_water_goal
    
    async def get_weekly_calorie_history(
        self,
        telegram_id: int
    ) -> list[CalorieHistoryDTO]:
        repo = Repository(self.db_session)
        user = await repo.get_user_by_telegram_id(telegram_id)
        if not user:
            return []
        today = date.today()
        week_ago = today - timedelta(days=7)
        history_db = await repo.get_calorie_history(
            user_id=user.id,
            start_date=week_ago,
            limit=7
        )
        history_dto = [
            CalorieHistoryDTO(
                date_info=stat.day,
                calories_consumed=stat.calories_consumed,
                calories_burned=stat.calories_burned
            )
            for stat in history_db
        ]
        return history_dto
    
    async def get_weekly_water_history(
        self,
        telegram_id: int
    ) -> list[WaterHistoryDTO]:
        repo = Repository(self.db_session)
        user = await repo.get_user_by_telegram_id(telegram_id)
        if not user:
            return []
        today = date.today()
        week_ago = today - timedelta(days=7)
        history_db = await repo.get_water_history(
            user_id=user.id,
            start_date=week_ago,
            limit=7
        )
        history_dto = [
            WaterHistoryDTO(
                date_info=stat.day,
                water_consumed=stat.water_consumed
            )
            for stat in history_db
        ]
        return history_dto
    
    async def _calculate_default_water_goal(
        self,
        weight: float,
        activity: int,
        city: str
    ) -> int:
        base = 30 * weight + activity / 30 * 500
        owm_client = OWMClient(api_key=OWM_API_KEY)
        weather = await owm_client.get_weather(city)
        if weather and weather.main.temp > 25:
            return base + 500
        return base
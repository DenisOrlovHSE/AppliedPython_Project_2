from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import (
    User,
    HealthProfile,
    DailyWaterStats,
    DailyCaloriesStats
)


class Repository:

    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        self.session = session

    async def add_user(
        self,
        telegram_id: int
    ) -> bool:
        try:
            new_user = User(telegram_id=telegram_id)
            self.session.add(new_user)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Failed to add user: {str(e)}")
            return False
    
    async def get_user_by_telegram_id(
            self,
            telegram_id: int
        ) -> User | None:
            result = await self.session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalars().first()
        
    async def update_health_profile(
        self,
        user_id: int,
        weight: float,
        height: float,
        age: int,
        activity: int,
        city: str,
        calorie_goal: int
    ) -> bool:
        try:
            result = await self.session.execute(
                select(HealthProfile).where(HealthProfile.user_id == user_id)
            )
            profile = result.scalars().first()
            if profile:
                profile.weight = weight
                profile.height = height
                profile.age = age
                profile.activity = activity
                profile.city = city
                profile.calorie_goal = calorie_goal
            else:
                new_profile = HealthProfile(
                    user_id=user_id,
                    weight=weight,
                    height=height,
                    age=age,
                    activity=activity,
                    city=city,
                    calorie_goal=calorie_goal
                )
                self.session.add(new_profile)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Failed to update health profile: {str(e)}")
            return False

    async def get_health_profile(
        self,
        user_id: int
    ) -> HealthProfile | None:
        result = await self.session.execute(
            select(HealthProfile).where(HealthProfile.user_id == user_id)
        )
        return result.scalars().first()
    
    async def update_daily_water_stats(
        self,
        user_id: int,
        day: date,
        water_goal: int,
        water_consumed: int | None = None
    ) -> DailyWaterStats | None:
        try:
            result = await self.session.execute(
                select(DailyWaterStats).where(
                    DailyWaterStats.user_id == user_id,
                    DailyWaterStats.day == day
                )
            )
            stats = result.scalars().first()
            if stats:
                if water_consumed is not None:
                    stats.water_consumed = water_consumed
                    stats.water_goal = water_goal
            else:
                new_stats = DailyWaterStats(
                    user_id=user_id,
                    day=day,
                    water_goal=water_goal,
                    water_consumed=water_consumed or 0
                )
                self.session.add(new_stats)
                stats = new_stats
            await self.session.commit()
            return stats
        except Exception as e:
            await self.session.rollback()
            print(f"Failed to update daily water stats: {str(e)}")
            return

    async def get_daily_water_stat(
        self,
        user_id: int,
        day: date
    ) -> DailyWaterStats | None:
        result = await self.session.execute(
            select(DailyWaterStats).where(
                DailyWaterStats.user_id == user_id,
                DailyWaterStats.day == day
            )
        )
        return result.scalars().first()
    
    async def update_daily_calories_stats(
        self,
        user_id: int,
        day: date,
        calories_goal: int,
        calories_consumed: int | None = None,
        calories_burned: int | None = None
    ) -> DailyCaloriesStats | None:
        try:
            result = await self.session.execute(
                select(DailyCaloriesStats).where(
                    DailyCaloriesStats.user_id == user_id,
                    DailyCaloriesStats.day == day
                )
            )
            stats = result.scalars().first()
            if stats:
                if calories_consumed is not None:
                    stats.calories_consumed = calories_consumed
                if calories_burned is not None:
                    stats.calories_burned = calories_burned
            else:
                new_stats = DailyCaloriesStats(
                    user_id=user_id,
                    day=day,
                    calories_goal=calories_goal,
                    calories_consumed=calories_consumed or 0,
                    calories_burned=calories_burned or 0
                )
                self.session.add(new_stats)
                stats = new_stats
            await self.session.commit()
            return stats
        except Exception as e:
            await self.session.rollback()
            print(f"Failed to update daily calories stats: {str(e)}")
            return

    async def get_daily_calories_stat(
        self,
        user_id: int,
        day: date
    ) -> DailyCaloriesStats | None:
        result = await self.session.execute(
            select(DailyCaloriesStats).where(
                DailyCaloriesStats.user_id == user_id,
                DailyCaloriesStats.day == day
            )
        )
        return result.scalars().first()
    
    async def get_calorie_history(
        self,
        user_id: int,
        start_date: date,
        limit: int = 30
    ) -> list[DailyCaloriesStats]:
        result = await self.session.execute(
            select(DailyCaloriesStats)
            .where(
                DailyCaloriesStats.user_id == user_id,
                DailyCaloriesStats.day >= start_date
            )
            .order_by(DailyCaloriesStats.day.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_water_history(
        self,
        user_id: int,
        start_date: date,
        limit: int = 30
    ) -> list[DailyWaterStats]:
        result = await self.session.execute(
            select(DailyWaterStats)
            .where(
                DailyWaterStats.user_id == user_id,
                DailyWaterStats.day >= start_date
            )
            .order_by(DailyWaterStats.day.desc())
            .limit(limit)
        )
        return result.scalars().all()
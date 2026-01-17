from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import Date, ForeignKey, UniqueConstraint
from datetime import datetime, date, timezone
from typing import List


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    
    health_profile: Mapped["HealthProfile"] = relationship("HealthProfile", back_populates="user", uselist=False)
    daily_water_stats: Mapped[List["DailyWaterStats"]] = relationship("DailyWaterStats", back_populates="user")
    daily_calories_stats: Mapped[List["DailyCaloriesStats"]] = relationship("DailyCaloriesStats", back_populates="user")


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    weight: Mapped[float] = mapped_column(nullable=False)
    height: Mapped[float] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    activity: Mapped[int] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    calorie_goal: Mapped[int] = mapped_column(nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="health_profile")


class DailyWaterStats(Base):
    __tablename__ = "daily_water_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False, default=datetime.now(timezone.utc).date())
    water_goal: Mapped[int] = mapped_column(nullable=False)
    water_consumed: Mapped[int] = mapped_column(nullable=False, default=0)

    user: Mapped["User"] = relationship("User", back_populates="daily_water_stats")
    
    __table_args__ = (UniqueConstraint("user_id", "day", name="unique_user_day"),)


class DailyCaloriesStats(Base):
    __tablename__ = "daily_calories_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False, default=datetime.now(timezone.utc).date())
    calories_goal: Mapped[int] = mapped_column(nullable=False)
    calories_consumed: Mapped[int] = mapped_column(nullable=False, default=0)
    calories_burned: Mapped[int] = mapped_column(nullable=False, default=0)

    user: Mapped["User"] = relationship("User", back_populates="daily_calories_stats")
    
    __table_args__ = (UniqueConstraint("user_id", "day", name="unique_user_day"),)
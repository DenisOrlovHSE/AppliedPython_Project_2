from aiogram.fsm.state import State, StatesGroup


class HealthProfileForm(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    calorie_goal = State()
    confirmation = State()


class LogFoodForm(StatesGroup):
    amount_in_grams = State()
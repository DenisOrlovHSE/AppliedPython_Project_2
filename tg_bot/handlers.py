from aiogram import Router, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service import Service
from tg_bot.states import HealthProfileForm, LogFoodForm
from . import messages
from .plotting import plot_calorie_history, plot_water_history


router = Router()


def setup_handlers(dp: Dispatcher):
    dp.include_router(router)


def get_back_restart_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="back"),
            InlineKeyboardButton(text="Начать заново", callback_data="restart")
        ]
    ])


def get_calorie_goal_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=messages.USE_DEFAULT_CALORIE_BUTTON, callback_data="use_default")],
        [InlineKeyboardButton(text="Назад", callback_data="back")],
        [InlineKeyboardButton(text="Начать заново", callback_data="restart")]
    ])


@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    service = Service(session)
    await service.create_user(message.from_user.id)
    await message.answer(messages.WELCOME_MESSAGE)


@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(HealthProfileForm.weight)
    await message.answer(messages.WEIGHT_PROMPT)


@router.message(Command("profile"))
async def cmd_set_profile(message: Message, session: AsyncSession):
    service = Service(session)
    profile = await service.get_health_profile(message.from_user.id)
    if not profile:
        await message.answer(messages.PROFILE_NOT_FOUND)
    else:
        await message.answer(messages.format_health_profile(profile))


@router.message(Command("progress"))
async def cmd_progress(message: Message, session: AsyncSession):
    service = Service(session)
    progress = await service.get_daily_progress(message.from_user.id)
    if not progress:
        await message.answer(messages.PROGRESS_NOT_FOUND)
    else:
        await message.answer(messages.format_daily_progress(progress))


@router.message(Command("log_water"))
async def cmd_log_water(message: Message, session: AsyncSession):
    service = Service(session)
    message_text = message.text.strip()
    parts = message_text.split()
    if len(parts) != 2:
        await message.answer(messages.LOG_WATER_USAGE)
        return
    try:
        amount = int(parts[1])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(messages.LOG_WATER_INVALID)
        return
    await service.log_water_consumption(message.from_user.id, amount=amount)
    await message.answer(messages.LOG_WATER_SUCCESS.format(amount=amount))


@router.message(HealthProfileForm.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight <= 0 or weight > 300:
            await message.answer(messages.WEIGHT_INVALID)
            return
        await state.update_data(weight=weight)
        await state.set_state(HealthProfileForm.height)
        await message.answer(
            messages.WEIGHT_CONFIRMATION.format(weight=weight),
            reply_markup=get_back_restart_keyboard()
        )
    except ValueError:
        await message.answer(messages.INVALID_NUMBER)


@router.callback_query(HealthProfileForm.weight)
async def back_restart_weight(query: CallbackQuery, state: FSMContext):
    if query.data == "restart":
        await state.clear()
        await state.set_state(HealthProfileForm.weight)
        await query.message.edit_text(messages.RESTART_MESSAGE, reply_markup=get_back_restart_keyboard())
    await query.answer()


@router.message(HealthProfileForm.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        if height <= 0 or height > 250:
            await message.answer(messages.HEIGHT_INVALID)
            return
        await state.update_data(height=height)
        await state.set_state(HealthProfileForm.age)
        await message.answer(
            messages.HEIGHT_CONFIRMATION.format(height=height),
            reply_markup=get_back_restart_keyboard()
        )
    except ValueError:
        await message.answer(messages.INVALID_NUMBER)


@router.callback_query(HealthProfileForm.height)
async def back_restart_height(query: CallbackQuery, state: FSMContext):
    if query.data == "back":
        await state.set_state(HealthProfileForm.weight)
        await query.message.edit_text(messages.BACK_TO_WEIGHT, reply_markup=get_back_restart_keyboard())
    elif query.data == "restart":
        await state.clear()
        await state.set_state(HealthProfileForm.weight)
        await query.message.edit_text(messages.RESTART_MESSAGE, reply_markup=get_back_restart_keyboard())
    await query.answer()


@router.message(HealthProfileForm.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 1 or age > 120:
            await message.answer(messages.AGE_INVALID)
            return
        await state.update_data(age=age)
        await state.set_state(HealthProfileForm.activity)
        await message.answer(
            messages.AGE_CONFIRMATION.format(age=age),
            reply_markup=get_back_restart_keyboard()
        )
    except ValueError:
        await message.answer(messages.INVALID_NUMBER)


@router.callback_query(HealthProfileForm.age)
async def back_restart_age(query: CallbackQuery, state: FSMContext):
    if query.data == "back":
        await state.set_state(HealthProfileForm.height)
        await query.message.edit_text(messages.BACK_TO_HEIGHT, reply_markup=get_back_restart_keyboard())
    elif query.data == "restart":
        await state.clear()
        await state.set_state(HealthProfileForm.weight)
        await query.message.edit_text(messages.RESTART_MESSAGE, reply_markup=get_back_restart_keyboard())
    await query.answer()


@router.message(HealthProfileForm.activity)
async def process_activity(message: Message, state: FSMContext):
    try:
        activity = int(message.text)
        if activity < 0 or activity > 1440:  # 1440 minutes = 24 hours
            await message.answer(messages.ACTIVITY_INVALID)
            return
        await state.update_data(activity=activity)
        await state.set_state(HealthProfileForm.city)
        await message.answer(
            messages.ACTIVITY_CONFIRMATION.format(activity=activity),
            reply_markup=get_back_restart_keyboard()
        )
    except ValueError:
        await message.answer(messages.INVALID_NUMBER)


@router.callback_query(HealthProfileForm.activity)
async def back_restart_activity(query: CallbackQuery, state: FSMContext):
    if query.data == "back":
        await state.set_state(HealthProfileForm.age)
        await query.message.edit_text(messages.BACK_TO_AGE, reply_markup=get_back_restart_keyboard())
    elif query.data == "restart":
        await state.clear()
        await state.set_state(HealthProfileForm.weight)
        await query.message.edit_text(messages.RESTART_MESSAGE, reply_markup=get_back_restart_keyboard())
    await query.answer()


@router.message(HealthProfileForm.city)
async def process_city(message: Message, state: FSMContext, session: AsyncSession):
    if len(message.text) < 2 or len(message.text) > 50:
        await message.answer(messages.CITY_INVALID)
        return
    
    await state.update_data(city=message.text)
    await state.set_state(HealthProfileForm.calorie_goal)

    service = Service(session)
    
    default_calories = service.calculate_default_calorie_goal(
        weight=(await state.get_data())['weight'],
        height=(await state.get_data())['height'],
        age=(await state.get_data())['age'],
        activity=(await state.get_data())['activity']
    )
    
    calorie_prompt = messages.CALORIE_GOAL_PROMPT.format(default_calories=default_calories)
    
    await message.answer(calorie_prompt, reply_markup=get_calorie_goal_keyboard())


@router.callback_query(HealthProfileForm.city)
async def back_restart_city(query: CallbackQuery, state: FSMContext):
    if query.data == "back":
        await state.set_state(HealthProfileForm.activity)
        await query.message.edit_text(messages.BACK_TO_ACTIVITY, reply_markup=get_back_restart_keyboard())
    elif query.data == "restart":
        await state.clear()
        await state.set_state(HealthProfileForm.weight)
        await query.message.edit_text(messages.RESTART_MESSAGE, reply_markup=get_back_restart_keyboard())
    await query.answer()


@router.message(HealthProfileForm.calorie_goal)
async def process_calorie_goal(message: Message, state: FSMContext):
    try:
        calorie_goal = int(message.text)
        if calorie_goal < 500 or calorie_goal > 10000:
            await message.answer(messages.CALORIE_GOAL_INVALID)
            return
        
        await state.update_data(calorie_goal=calorie_goal)
        data = await state.get_data()
        
        await state.set_state(HealthProfileForm.confirmation)
        
        confirmation_text = messages.get_confirmation_text(
            data['weight'], data['height'], data['age'], 
            data['activity'], data['city'], calorie_goal
        )
        
        confirmation_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Всё верно!", callback_data="confirm_yes")],
            [InlineKeyboardButton(text="Назад", callback_data="back")],
            [InlineKeyboardButton(text="Начать заново", callback_data="restart")]
        ])
        
        await message.answer(confirmation_text, reply_markup=confirmation_kb)
    except ValueError:
        await message.answer(messages.INVALID_NUMBER)


@router.callback_query(HealthProfileForm.calorie_goal)
async def process_calorie_default(query: CallbackQuery, state: FSMContext, session: AsyncSession):
    service = Service(session)
    data = await state.get_data()
    
    if query.data == "use_default":
        default_calories = service.calculate_default_calorie_goal(
            weight=data['weight'],
            height=data['height'],
            age=data['age'],
            activity=data['activity']
        )
        await state.update_data(calorie_goal=default_calories)
        
        await state.set_state(HealthProfileForm.confirmation)
        
        confirmation_text = messages.get_confirmation_text(
            data['weight'], data['height'], data['age'], 
            data['activity'], data['city'], default_calories
        )
        
        confirmation_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Всё верно!", callback_data="confirm_yes")],
            [InlineKeyboardButton(text="Назад", callback_data="back")],
            [InlineKeyboardButton(text="Начать заново", callback_data="restart")]
        ])
        
        await query.message.edit_text(confirmation_text, reply_markup=confirmation_kb)
    
    elif query.data == "back":
        await state.set_state(HealthProfileForm.city)
        await query.message.edit_text(messages.BACK_TO_CITY, reply_markup=get_back_restart_keyboard())
    
    elif query.data == "restart":
        await state.clear()
        await state.set_state(HealthProfileForm.weight)
        await query.message.edit_text(messages.RESTART_MESSAGE, reply_markup=get_back_restart_keyboard())
    
    await query.answer()


@router.callback_query(HealthProfileForm.confirmation)
async def process_confirmation(query: CallbackQuery, state: FSMContext, session: AsyncSession):
    service = Service(session)
    data = await state.get_data()
    if query.data == "confirm_yes":
        
        success = await service.update_health_profile(
            telegram_id=query.from_user.id,
            weight=data['weight'],
            height=data['height'],
            age=data['age'],
            activity=data['activity'],
            city=data['city'],
            calorie_goal=data.get('calorie_goal')
        )
        
        if success:
            await query.message.edit_text(messages.PROFILE_SAVED_SUCCESS)
            await state.clear()
        else:
            await query.message.edit_text(messages.PROFILE_SAVE_ERROR)
    
    elif query.data == "back":
        await state.set_state(HealthProfileForm.calorie_goal)
        await query.message.edit_text(messages.CALORIE_GOAL_PROMPT.format(default_calories=service.calculate_default_calorie_goal(
            weight=data['weight'],
            height=data['height'],
            age=data['age'],
            activity=data['activity']
        )), reply_markup=get_calorie_goal_keyboard())
    
    elif query.data == "restart":
        await state.clear()
        await state.set_state(HealthProfileForm.weight)
        await query.message.edit_text(messages.RESTART_MESSAGE, reply_markup=get_back_restart_keyboard())
    
    await query.answer()


@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    service = Service(session)
    message_text = message.text.strip()
    parts = message_text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer(messages.LOG_FOOD_USAGE)
        return
    food_name = parts[1]
    calories_per_100g = await service.get_food_calories_per_100g(food_name)
    await state.set_state(LogFoodForm.amount_in_grams)
    await state.update_data(food_name=food_name, calories_per_100g=calories_per_100g)
    
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_log_food")]
    ])
    
    await message.answer(messages.LOG_FOOD_PROMPT.format(food_name=food_name, calories_per_100g=calories_per_100g), reply_markup=cancel_kb)


@router.message(LogFoodForm.amount_in_grams)
async def process_food_amount(message: Message, state: FSMContext, session: AsyncSession):
    try:
        amount_in_grams = int(message.text)
        if amount_in_grams <= 0:
            await message.answer(messages.LOG_FOOD_INVALID)
            return
        data = await state.get_data()
        service = Service(session)
        success, total_calories = await service.log_food_consumption(
            telegram_id=message.from_user.id,
            amount_in_grams=amount_in_grams,
            calories_per_100g=data['calories_per_100g']
        )
        if success:
            await message.answer(messages.LOG_FOOD_SUCCESS.format(calories=total_calories))
        else:
            await message.answer(messages.LOG_FOOD_FAILURE)
        await state.clear()
    except ValueError:
        await message.answer(messages.LOG_FOOD_INVALID)


@router.callback_query(LogFoodForm.amount_in_grams)
async def cancel_log_food(query: CallbackQuery, state: FSMContext):
    if query.data == "cancel_log_food":
        await query.message.edit_text(messages.LOG_FOOD_CANCELLED)
        await state.clear()
    await query.answer()


@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message, session: AsyncSession):
    service = Service(session)
    message_text = message.text.strip()
    parts = message_text.split()
    if len(parts) != 3:
        await message.answer(messages.LOG_WORKOUT_USAGE)
        return
    try:
        workout_type = parts[1]
        duration_minutes = int(parts[2])
        if duration_minutes <= 0:
            raise ValueError
    except ValueError:
        await message.answer(messages.LOG_WORKOUT_INVALID)
        return
    result = await service.log_workout(message.from_user.id, exercise_name=workout_type, duration_minutes=duration_minutes)
    success, burned_calories, additional_water_goal = result
    if not success:
        await message.answer(messages.LOG_WORKOUT_FAILURE)
    else:
        await message.answer(messages.LOG_WORKOUT_SUCCESS.format(burned_calories=burned_calories, additional_water_goal=additional_water_goal))


@router.message((Command("workouts")))
async def cmd_workouts(message: Message, session: AsyncSession):
    service = Service(session)
    workout_types = service.workout_manager.get_all_exercises()
    workouts_text = messages.get_available_workouts_text(workout_types)
    await message.answer(workouts_text)


@router.message(Command("weekly_water"))
async def cmd_weekly_water(message: Message, session: AsyncSession):
    service = Service(session)
    profile = await service.get_health_profile(message.from_user.id)
    if not profile:
        await message.answer(messages.PROFILE_NOT_FOUND)
        return
    water_data = await service.get_weekly_water_history(message.from_user.id)
    if not water_data:
        await message.answer(messages.PROGRESS_NOT_FOUND)
        return
    plot_bytes = plot_water_history(water_data)
    photo = BufferedInputFile(plot_bytes, filename="water_history.png")
    await message.answer_photo(photo)


@router.message(Command("weekly_calories"))
async def cmd_weekly_calories(message: Message, session: AsyncSession):
    service = Service(session)
    profile = await service.get_health_profile(message.from_user.id)
    if not profile:
        await message.answer(messages.PROFILE_NOT_FOUND)
        return
    calorie_data = await service.get_weekly_calorie_history(message.from_user.id)
    if not calorie_data:
        await message.answer(messages.PROGRESS_NOT_FOUND)
        return
    plot_bytes = plot_calorie_history(calorie_data)
    photo = BufferedInputFile(plot_bytes, filename="calorie_history.png")
    await message.answer_photo(photo)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(messages.HELP_MESSAGE)
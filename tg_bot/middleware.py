from aiogram import Dispatcher
from database.session import AsyncSessionLocal


def setup_middleware(dp: Dispatcher):
    dp.message.middleware(get_session_middleware)
    dp.message.middleware(log_middleware)
    dp.callback_query.middleware(get_session_middleware)
    dp.callback_query.middleware(log_middleware)


async def get_session_middleware(handler, event, data):
    async with AsyncSessionLocal() as session:
        data["session"] = session
        return await handler(event, data)


async def log_middleware(handler, event, data):
    if hasattr(event, 'message'):
        print(
            f"CallbackQuery from user {event.from_user.id} "
            f"({event.from_user.first_name}): {event.data}"
        )
    else:
        print(
            f"Message from user {event.from_user.id} "
            f"({event.from_user.first_name}): {event.text}"
        )
    
    return await handler(event, data) 
    
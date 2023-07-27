from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from services.redis_server import check_user_id_in_redis, check_and_create_structure_reports


# Это будет inner-мидлварь на сообщения
class CheckUserMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        # проверяем, есть ли пользователь в базе данных
        if await check_user_id_in_redis(event.from_user.id):
            return await handler(event, data)
        # В противном случае просто вернётся None
        # и обработка прекратится
        await event.answer("Вы не зарегистрированы!\n\n"
                           "для регистрации напишите или нажмите кнопку /start\n\n"
                           "CheckUserMessageMiddleware", show_alert=True)
        return


# Это будет outer-мидлварь на любые колбэки
class CheckUserCallbackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        # проверяем, есть ли пользователь в базе данных
        if await check_user_id_in_redis(event.from_user.id) or event.data == 'create_company':
            # проверяем структуры бд
            if await check_user_id_in_redis(event.from_user.id):
                await check_and_create_structure_reports(event.from_user.id)
            return await handler(event, data)
        # В противном случае отвечаем на колбэк самостоятельно
        # и прекращаем дальнейшую обработку
        await event.answer("Вы не зарегистрированы!\n\n"
                           "для регистрации напишите или нажмите кнопку /start\n\n"
                           "CheckUserCallbackMiddleware", show_alert=True)
        await event.answer()
        return

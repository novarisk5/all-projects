import asyncio
from aiogram import Bot, Dispatcher

from app.handlers import router
from app.database.models import async_main
from aiogram import Bot
import app.keyboards as kb
import app.database.requests as rq


async def main():
    await async_main()
    bot = Bot(token='8332435452:AAG1mXYAgeiphBtR7xkJpoRz022Ab4i4bm8')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
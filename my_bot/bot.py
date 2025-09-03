import asyncio
from aiogram import Bot, Dispatcher
from app.config import config
from app.handlers import all_routers
from app.logger import setup_logging, get_logger

log = get_logger('bot')

async def main():
    
    setup_logging()#запускаем конфиг логов
    
    if not config.BOT_TOKEN: #проверка на установку в токена
        raise ValueError("BOT_TOKEN не установлен! проверьте .env файл")
    
    log.info('запуск бота...')
    bot = Bot(token=config.BOT_TOKEN)#бот с переданным токеном
    dp = Dispatcher()# ядро нашего бота, принимаюший обновления, определяет тип сообщения находит обработчик и тд
    
    for router in all_routers: 
        dp.include_router(router)#подключаем роутеры в диспетчер

    
    try:
        await dp.start_polling(bot)#начинаем опрашивать бота 
    except Exception: 
        log.exception('критичкая ошибка polling')
    finally: 
        log.info('Остановка бота')

if __name__ == "__main__":#если файл запущен напрямую
    asyncio.run(main())#начинаем событийный цикл
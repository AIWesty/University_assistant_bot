from aiogram import Router, types, F 
from aiogram.filters import Command
from app.keyboards.main_keyboard import main_menu 

from app.logger import get_logger
log = get_logger(__name__)

router = Router() #маршрутизатор  для обработки сообщений. Он группирует обработчики для определенных типов сообщений.

@router.message(Command('start', 'начать'))
async def cmd_start(message: types.Message): 
    if message.from_user:
        log.info("Пользователь %s (%s) вызвал /start", message.from_user.id, message.from_user.username)
    '''функция обработчик команды /start'''
    
    WELCOME = (
    "Привет! Я помогу с поступлением:\n"
    "• Частые вопросы — «FAQ»\n"
    "• Подать заявку — «📋 Заявка»\n"
    "• Оставить отзыв — «💬 Оставить отзыв»\n\n"
    "Также доступна команда /help."
        )
    #формируем ответ бота
    await message.answer(text=WELCOME, reply_markup=main_menu)

@router.message(F.text == "Привет")#обработка текста "привет", с клавиатуры
async def button_hello(message: types.Message):
    await message.answer("Привет, рад тебя видеть! 👋")#ответ
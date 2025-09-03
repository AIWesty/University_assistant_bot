from aiogram import Router, types, F
from aiogram.filters import Command
from app.keyboards.main_keyboard import main_menu

from app.logger import get_logger
log = get_logger(__name__)

router = Router()#роутер для обработки сообщения

@router.message(Command('help', 'помощь'))#обрабатываем команду help
@router.message(F.text == 'Помощь')
async def cmd_help(message: types.Message):
    if message.from_user: 
        log.info("Пользователь %s запросил /help", message.from_user.id)
        text = (
        "👋 Я бот приёмной комиссии.\n\n"
        "Вот что я умею:\n"
        "📚 ℹ️ Информация о факультете — расскажу об университете\n"
        "📄 Документы — список, что нужно для поступления\n"
        "📊 Проходные баллы — статистика прошлых лет\n"
        "📅 Сроки подачи — когда подавать документы\n"
        "📝 Подать заявку — заполнить анкету прямо здесь\n"
        "💬 Оставить отзыв — поделиться вашим мнением\n\n"
        "❓ Раздел FAQ - ответы на основные вопросы"
    )
    await message.answer(text, reply_markup=main_menu)
from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from app.services.faq_service import get_all_questions, get_answer_by_id
from app.keyboards.faq_keyboard import build_keyboard_faq
from app.logger import get_logger

router = Router()
logger = get_logger(__name__)


# Пользователь нажимает кнопку "❓ FAQ"
@router.message(F.text == "❓ FAQ")
async def show_faq(message: types.Message):
    faq_list = await get_all_questions()#делаем запрос на выборку
    if not faq_list:#если ничего не выбрали
        await message.answer("❓ Пока нет вопросов в базе.")
        return

    kb = build_keyboard_faq(faq_list)  # inline кнопки faq_{id}, делаем клавиатуру из вопросов
    await message.answer("📖 Выберите интересующий вас вопрос:", reply_markup=kb)#кидаем ответ с клавой


# Пользователь выбирает вопрос
@router.callback_query(F.data.startswith("faq_"))#ообработка конкретного вопрос, происходит все из за callback данных от нажатия inline кнопки
async def show_faq_answer(callback: CallbackQuery):
    if not callback.data or not callback.message:
        return

    try:
        #пытаемся поделить вернувшиеся данные 
        parts = callback.data.split("_")
        #если их длина 2 и вторая часть - число
        if len(parts) == 2 and parts[1].isdigit():
            faq_id = int(parts[1])#берем айдишник(вторую часть)
            answer = await get_answer_by_id(faq_id)#и пытаемся по нему сделать выборку ответа из таблицы с faq

            if answer:#если выбрали
                await callback.message.answer(f"💡 {answer}")#посылаем ответ
                logger.info("Пользователь %s получил ответ на FAQ %s", callback.from_user.id, faq_id)
            else:
                await callback.message.answer("⚠️ Ответа на этот вопрос пока нет.")
        else:
            #иначе некорректный запрос, показываем с анимацией
            await callback.answer("Некорректный запрос FAQ", show_alert=True)

    except Exception as e:
        await callback.message.answer("❌ Ошибка обработки запроса.")
        logger.error("Ошибка обработки FAQ: %s", e)

    await callback.answer()
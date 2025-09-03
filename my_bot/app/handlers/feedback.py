from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states.feedback import FeedbackForm
from app.database import engine, feedback

from app.logger import get_logger
log = get_logger(__name__)

router = Router() 

@router.message(Command('/feedback')) #тут обрабатываем конкретно команду/текст на который нужно среагировать
@router.message(F.text == '💬 Оставить отзыв')
async def start_feedback_cmd(message: types.Message, state: FSMContext): #функция обработки команды оставить отзыв
    await message.answer("✍️ Напишите свой отзыв или предложение:")
    await state.set_state(FeedbackForm.message)#меняем состяние на FeedbackForm

#здесь принимаем состояние сообщения
@router.message(FeedbackForm.message)
async def process_mess_feedback(message: types.Message, state: FSMContext): #принимаем состояние
    if message.from_user is not None: 
        tg_id = message.from_user.id
    text = (message.text or "").strip()#из пришедшего сообщения извлекаем текст
    
    if not text: 
        await message.answer('❌ Отзыв пустой. Напишите хотя бы пару слов 🙂')#если текста нет
        return
    try: 
        async with engine.begin() as conn: 
            await conn.execute(
                feedback.insert().values(
                    tg_id=tg_id,
                    message=text
                )#пытаемся в базу сохранить отзыв
            )
        log.info("Feedback saved: tg_id=%s len=%d", tg_id, len(text))#логируем сохранение 
        await message.answer("✅ Спасибо за отзыв! Он сохранён в системе 🙌")
    except Exception:#обрабатываем исключения
        log.exception("Не удалось сохранить feedback: tg_id=%s", tg_id)
        await message.answer("⚠️ Не удалось сохранить отзыв, попробуй позже.")
    finally:
        await state.clear()#закрываем состояния
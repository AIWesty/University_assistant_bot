from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram import types
from app.config import config
from app.logger import get_logger
from app.states.admin import AdminReply, AdminFaq
from app.keyboards.admins_kb import admin_main_kb, form_actions_kb, feedback_actions_kb, faq_admin_kb

from app.database import engine, form, feedback, faq, admin_messages  # таблицы
from sqlalchemy import select, update, delete, insert
from app.keyboards.faq_keyboard import build_keyboard_faq
from app.services.faq_service import add_faq, get_all_questions

router = Router()
log = get_logger(__name__)
# проверка админа
def is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids

# точка входа, обработка /admin
@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    user = message.from_user
    if not user or not is_admin(user.id):
        await message.answer("Доступ запрещён. Эта команда только для администраторов.")
        return

    await message.answer("🔐 Админ-панель", reply_markup=admin_main_kb())#прокидываем основную клаву админа с callback датой

# Обработка кликов в админ-меню
@router.callback_query(F.data == "admin_apps")#обрабатываем нажатия  "заявки" при попощи callback
async def admin_list_apps(callback: CallbackQuery):
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    if not callback.message:
        return

    # получаем последние 10 заявок
    async with engine.connect() as conn:
        result = await conn.execute(
            select(form.c.id, form.c.name, form.c.direction, form.c.phone_number, form.c.created_at)
            .order_by(form.c.created_at.desc())
            .limit(10)
        )
        rows = result.mappings().all()# преобразует результат SQL-запроса в список словарей

    if not rows:#если ничего не выбрали
        await callback.message.answer("Нет заявок.")
        await callback.answer()
        return

    # Формируем список и кнопки
    for row in rows:
        app_id = row["id"]#айдишник заявки
        text = (
            f"#{app_id} • {row['name']}\n"
            f"Направление: {row['direction']}\n"
            f"Телефон: {row['phone_number']}\n"
            f"Дата: {row['created_at']:%Y-%m-%d %H:%M}\n"
        )
        await callback.message.answer(text, reply_markup=form_actions_kb(app_id))#отдаем в ответе текст и клаву действий

    await callback.answer()#прекращаем ожидание на кнопке

# Показ деталей заявки (можно по callback сделать отдель view, но мы показываем в списке)
# Обработчик Reply -> ответить; мы начинаем FSM AdminReply и запомним application_id и user_tg_id
@router.callback_query(F.data.startswith("app_reply:"))
async def admin_app_reply(callback: CallbackQuery, state: FSMContext):
    admin_id = callback.from_user.id
    if not is_admin(admin_id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    if not callback.data:
        return
    if not callback.message:
        return
    
    app_id = int(callback.data.split(":")[1])

    # вытащим информацию о заявке, в частности user_id/tg_id
    async with engine.connect() as conn:
        #делаем выборку айди человека, по айди его заявки
        result = await conn.execute(select(form.c.user_id).where(form.c.id == app_id))
        row = result.fetchone()
    #если не выбрали
    if not row:
        await callback.message.answer("Заявка не найдена.")
        await callback.answer()
        return 
    
    user_tg_id = row[0]  # здесь в form мы сохранили user_id как telegram id (смотри модель)

    # сохраняем контекст (form id, user id)
    await state.update_data(reply_to_app=app_id, reply_to_user=user_tg_id)
    await state.set_state(AdminReply.to_user)

    await callback.message.answer(f"Напишите сообщение пользователю (tg_id={user_tg_id}). Оно будет отправлено как от имени бота.")
    await callback.answer()

# Получаем текст от админа и пересылаем пользователю
@router.message(AdminReply.to_user)
async def admin_send_reply(message: types.Message, state: FSMContext, bot: Bot):
    admin = message.from_user
    if not admin or not is_admin(admin.id):
        await message.answer("Доступ запрещён.")
        await state.clear()
        return
    

    data = await state.get_data()#обновляем данные состояния 
    app_id = data.get("reply_to_app")#получаем айди заявки
    user_tg_id = data.get("reply_to_user")#айди юзера 
    text = message.text or ""#текст который нужно переслать

    try:
        # отправляем пользователю
        if user_tg_id:
            await bot.send_message(user_tg_id, f"📣 Ответ от приёмной комиссии:\n\n{text}")
        # сохраняем в БД лог admin_messages 
        async with engine.begin() as conn:
            await conn.execute(
                insert(admin_messages).values(
                    admin_id=admin.id, user_tg_id=user_tg_id, application_id=app_id, message=text
                )
            )

        await message.answer("✅ Ответ отправлен пользователю.")
        log.info("Admin %s ответил пользователю %s (app %s)", admin.id, user_tg_id, app_id)
    except Exception as e:
        log.exception("Не удалось отправить сообщение пользователю %s: %s", user_tg_id, e)
        await message.answer("⚠️ Не удалось отправить сообщение — возможно пользователь заблокировал бота или неверный tg_id.")

    await state.clear()

# Отметить заявку обработанной
@router.callback_query(F.data.startswith("app_done:"))
async def admin_mark_done(callback: CallbackQuery):
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    if not callback.data:
        return
    if not callback.message:
        return

    #получаем айди заявки из кнопки
    app_id = int(callback.data.split(":")[1])
    async with engine.begin() as conn:
        result = await conn.execute(#делаем обновление состояния для задачи - выполнено(обработано)
            update(form).where(form.c.id == app_id).values(status="done").returning(form.c.id)
        )
        updated = result.scalar_one_or_none()#возвращаем либо обнвленное значение либо ничего

    if updated:#если да 
        await callback.answer("Заявка помечена как обработанная ✅")#то отвечаем
        # await callback.message.edit_reply_markup(None)
        log.info("Admin %s пометил заявку %s как done", callback.from_user.id, app_id)
    else:
        await callback.answer("Не удалось пометить. Возможно, заявка уже помечена или не существует.", show_alert=True)

# Удалить заявку
@router.callback_query(F.data.startswith("app_del:"))
async def admin_delete_app(callback: CallbackQuery):
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    if not callback.data: 
        return 
    #выбираем айдишник заявки из данных callback
    app_id = int(callback.data.split(":")[1])
    async with engine.begin() as conn:#открываем соединение 
        #удаляем заявку по айдишнику
        result = await conn.execute(delete(form).where(form.c.id == app_id).returning(form.c.id))
        deleted = result.scalar_one_or_none()#возвращаем удаленное 

    if deleted:#если удалилось
        await callback.answer("Заявка удалена 🗑")
        # await callback.message.edit_reply_markup(None)
        log.info("Admin %s удалил заявку %s", callback.from_user.id, app_id)#логируем
    else:
        await callback.answer("Не удалось удалить заявку.", show_alert=True)

# --- Feedback: просмотр и удаление
@router.callback_query(F.data == "admin_feedback")
async def admin_list_feedback(callback: CallbackQuery):
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    if not callback.message:
        return
    
    #открываем соединение
    async with engine.connect() as conn:
        #делаем выборку отзывов 
        result = await conn.execute(select(feedback.c.id, feedback.c.message, feedback.c.created_at).order_by(feedback.c.created_at.desc()).limit(10))
        rows = result.mappings().all()#группируем в словари

    #если нет отзывов
    if not rows:
        await callback.message.answer("Нет отзывов.")
        await callback.answer()
        return

    for row in rows:
        #формируем ответ
        text = f"#{row['id']} • {row['created_at']:%Y-%m-%d %H:%M}\n{row['message']}"
        #отвечаем текстом с клавой
        await callback.message.answer(text, reply_markup=feedback_actions_kb(row['id']))

    await callback.answer()

#удаление отзыва
@router.callback_query(F.data.startswith("fb_del:"))
async def admin_delete_feedback(callback: CallbackQuery):
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    if not callback.data: 
        return

    fid = int(callback.data.split(":")[1])
    async with engine.begin() as conn:#открываем соединение 
        #удаляем отзыв по айдишнику
        result = await conn.execute(delete(feedback).where(feedback.c.id == fid).returning(feedback.c.id))
        deleted = result.scalar_one_or_none()#вощвращаем его 

    if deleted:#если удалили 
        await callback.answer("Отзыв удалён 🗑")
        # await callback.message.edit_reply_markup(None)
        log.info("Admin %s удалил feedback %s", callback.from_user.id, fid)
    else:
        await callback.answer("Не удалось удалить отзыв.", show_alert=True)

# Админ заходит в меню FAQ
@router.callback_query(F.data == "admin_faq")
async def admin_faq_menu(callback: CallbackQuery):
    #проверка на то что это делает админ
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return

    if not callback.message:
        return
    await callback.message.answer("Управление FAQ:", reply_markup=faq_admin_kb())
    await callback.answer()

#просмотр всех FAQ
#здесь мы разграничили доступ, сюда попадаем только если человек админ
@router.callback_query(F.data == 'admin_faq_list')
async def show_all_faq_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    if not callback.message:
        return  
    
    #выборка всех ответов-вопросов
    faq_list = await get_all_questions()
    if not faq_list:
        await callback.message.answer("❓ В базе пока нет FAQ.")
        return
    #делаем клаву
    kb = build_keyboard_faq(faq_list)
    await callback.message.answer("📖 Все вопросы из базы:", reply_markup=kb)#возврат ответа и клавиатуры
    await callback.answer()



#добавление в faq
@router.callback_query(F.data == "admin_faq_add")#смотрим по конкретной callback дате
async def admin_faq_add_start(callback: CallbackQuery, state: FSMContext):
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    if not callback.message:
        return 
    #обновляем данные состояния 
    await state.update_data(start_message_id=callback.message.message_id)
    await state.set_state(AdminFaq.adding_question)#меняем состояние на добавление 
    await callback.message.answer("Введите текст вопроса:")
    await callback.answer()
    
#добавление конкретного вопроса
@router.message(AdminFaq.adding_question)
async def admin_faq_add_question(message: types.Message, state: FSMContext):
    if not message.from_user or not is_admin(message.from_user.id):
        await message.answer("Доступ запрещён.")
        await state.clear()
        return
    #обновляем данные, сохраняя вопрос
    await state.update_data(new_question=message.text)
    await state.set_state(AdminFaq.adding_answer)#переходим в добавление ответа
    await message.answer("Теперь введите ответ на этот вопрос:")

#добавляем ответ на вопрос
@router.message(AdminFaq.adding_answer)
async def admin_faq_add_answer(message: types.Message, state: FSMContext):
    if not message.from_user or not is_admin(message.from_user.id):
        await message.answer("Доступ запрещён.")
        await state.clear()
        return
    #получаем данные вопроса и ответа
    data = await state.get_data()
    q = data.get("new_question")#вопрос берем из данных 
    a = message.text# ответ из пришедшего сообщения
    if not q or not a: 
        return
    # Запишем в БД, но предварительно проверим дубль
    await add_faq(q, a)#запишем новый вопрос и ответ
    await message.answer("✅ Вопрос добавлен в FAQ.")
    log.info("Admin %s добавил FAQ: %s", message.from_user.id, q)
    await state.clear()
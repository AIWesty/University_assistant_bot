from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, update, delete
from app.states.tasks import AddTask
from aiogram.fsm.context import FSMContext
from app.database import engine, tasks

from app.logger import get_logger
log = get_logger(__name__)#инициализировали логгер и дали ему имя


#описали роутер
router = Router() 

@router.message(Command('add_task'))
async def start_add_task_cmd(message: types.Message, state: FSMContext): 
    """принимаем команду и отвечаем сообщением, затем меняем состояние"""
    if message.from_user:
        log.info("Пользователь %s начал добавление задачи", message.from_user.id)
    await message.answer('Давай добавим задачу. Напиши текст задачи одним сообщением:')
    await state.set_state(AddTask.title)

@router.message(F.text == 'Добавить задачу')
async def start_add_task_btn(message: types.Message, state: FSMContext):
    """функция обработки кнопки добавить задачу, вызывает функцию добавления задачи"""
    await start_add_task_cmd(message, state)

@router.message(AddTask.title)#принимаем состояние
async def save_task(message: types.Message, state: FSMContext): 
    """функция сохранения задачи"""
    title = (message.text or '').strip() #берем текст задачи 
    
    #проверяем данные 
    if message.from_user is not None:
        tg_id = message.from_user.id
        
    if not title: #если задача пустая
        await message.answer("Текст задачи пустой. Напиши, что нужно сделать:")
        log.warning("Пользователь %s отправил пустую задачу", tg_id)
        return
    
    try:
        async with engine.begin() as conn: #открываем соединение 
            await conn.execute(# выполняем запрос
                tasks.insert().values(# проводим вставку данных со значениями
                    tg_id=tg_id,
                    title=title,
                    status='new'
                )
            )
        log.info("Добавлена задача: tg_id=%s title=%r", tg_id, title)
        await message.answer('✅ Задача добавлена!\n\nНапиши «Мои задачи» или нажми кнопку, чтобы посмотреть список.')
    except Exception: 
        log.exception("Не удалось сохранить задачу: tg_id=%s title=%r", tg_id, title)
        await message.answer("⚠️ Не удалось сохранить задачу, попробуй позже.")
    await state.clear() #закрываем состояния

    
@router.message(Command("my_tasks"))
@router.message(F.text == "Мои задачи")#откличкаемся на команду и на текст
async def show_tasks(message: types.Message): 
    if message.from_user is not None:
        tg_id = message.from_user.id #будем ловить запросы по id, чтобы изолировать данные 
        
    log.info("Пользователь %s запросил список задач", tg_id)
    async with engine.begin() as conn: #открываем соединение 
        result = await conn.execute(#сохраняем его в переменную
            select(
                tasks.c.id, tasks.c.title, tasks.c.status, tasks.c.created_at#выбираем нужные столбцы
            ).where(tasks.c.tg_id == tg_id).order_by(tasks.c.created_at.desc())#выбираем для конкретного пользователя и группируем
        )
        rows = result.mappings().all()#делаем из задач словари
        
        if not rows: 
            await message.answer('У тебя пока нет задач. Нажми «Добавить задачу» и создай первую!"')
            return
        
        lines = []
        kb = InlineKeyboardBuilder() #создатель интерактивной клавиатуры
        for row in rows: #пробегаемся по задачам
            status_emoji = "🟢" if row["status"] == "new" else "✅"#выбираем эмодзи
            lines.append(f"{status_emoji} {row['title']}")#добавляем в список с задачами статус и описание
            #если задача активна(создана) для нее нужны кнопки
            if row['status'] == 'new': 
                kb.button(text="✅ Выполнено", callback_data=f"task_done:{row['id']}")#добавляем кнопку выполнено
                kb.button(text="🗑 Удалить", callback_data=f"task_del:{row['id']}")#и кнопку удалить, с возвращаемыми данными
                kb.adjust(2)#кнопки в ряд 
                
        #обьединяем все задачи в текст
        text = "📋 *Твои задачи:*\n\n" + "\n".join(lines)
        #отвечаем пользователю с форматированием, прикрепляя клавиатуру 
        await message.answer(text, parse_mode='Markdown', reply_markup=kb.as_markup())
    
@router.callback_query(F.data.startswith("task_done:"))#реагируем на callback с task_done:
async def task_done_db(callback: types.CallbackQuery): 
    try:
        if callback.data is not None:
            task_id = int(callback.data.split(":")[1])#пробуем извлечь айди задачи
    except Exception:#отлавливаем исключение 
        await callback.answer("Некорректный идентификатор задачи.", show_alert=True)#ответ
        log.warning('пользователь ввел некорректный индентификатор задачи')
        return
    if callback.from_user is not None: #обработка юзера
        tg_id = callback.from_user.id
    
    try:
        async with engine.begin() as conn: #открывает транзакцию
            result = await conn.execute(
                update(tasks)#обновить данные
                .where(tasks.c.id == task_id, tasks.c.tg_id == tg_id, tasks.c.status == 'new')#фильтрация по айди задачи, человека, и статуса
                .values(
                    status='done'#поменять значение на 
                )
                .returning(
                    tasks.c.id#вернуть id задачи
                )
            )
        updated = result.scalar_one_or_none()#получаем айди или None если транзация отклонилась
        log.info("Задача отмечена как выполненная tg_id=%s task_id=%r", tg_id, task_id)
        if updated is None: #если none 
            await callback.answer("Не удалось отметить. Возможно, задача уже выполнена или не твоя.", show_alert=True)
            log.warning("Задачу task_id=%r пользователя tg_id=%s не удалось отметить", tg_id, task_id)
        else: 
            await callback.answer("Готово! Задача отмечена как выполненная ✅")
    except Exception:
        log.error("произошла ошибка выполнения задачи task_id=%r пользователя tg_id=%s", tg_id, task_id)

@router.callback_query(F.data.startswith('task_del'))
async def task_del_db(callback: types.CallbackQuery): 
    if callback.from_user is not None: #обработка юзера
        tg_id = callback.from_user.id
    
    try:
        if callback.data is not None:
            task_id = int(callback.data.split(":")[1])#пробуем извлечь айди задачи
    except Exception:#отлавливаем исключение 
        await callback.answer("Некорректный идентификатор задачи.", show_alert=True)#ответ
        log.warning('Пользователь ввел некорректный идентификатор задачи')
        return
    try:
        
        async with engine.begin() as conn: #соединение 
            result = await conn.execute(#исполняем
                delete(tasks)#удаление 
                .where(tasks.c.id == task_id, tasks.c.tg_id == tg_id)#где айди задачи совпадает с переданным
                .returning(tasks.c.id)#возвращаем айди задачи
            )
        
        deleted = result.scalar_one_or_none()#айди или none 
        if deleted is None: 
            log.error('Не удалось удалить. Возможно, это не та задача task_id=%r tg_id=%s',  tg_id, task_id)
            await callback.answer("Не удалось удалить. Возможно, это не твоя задача.", show_alert=True)
        else:
            log.error('Задача task_id=%r пользователя tg_id=%s удалена',  tg_id, task_id)
            await callback.answer("Задача удалена 🗑")
    except Exception: 
        log.error('Не получилось удалить задачу task_id=%r пользователя tg_id=%s',  tg_id, task_id)
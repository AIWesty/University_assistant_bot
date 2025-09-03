from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext #для обработки состояний 
from app.states.form import Form #класс с нашей формой(состояниями)
from app.database import form, engine
from aiogram.types import ReplyKeyboardRemove
from app.keyboards.main_keyboard import main_menu
import re

#идеи - сохранять состояния после ответов пользователя, сохраняя контекст, и сохраняя данные приходящие
#от пользователей
from app.logger import get_logger
log = get_logger(__name__)

# --- helpers ---
PHONE_HINT = (
    "📱 Введите номер телефона в международном формате, например:\n"
    "+79991234567 или 89991234567"
)
EMAIL_HINT = "✉️ Укажите ваш email (например, name@example.com):"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Допустим любые номера длиной 10–15 цифр, с необязательным + в начале
PHONE_RE = re.compile(r"^\+?\d{10,15}$")




router = Router() 

@router.message(Command('form'))#обработка команды формы
@router.message(F.text == '📋 Заявка')
async def cmd_form(message: types.Message, state: FSMContext): 
    if message.from_user:
        log.info("Анкета начата пользователем %s", message.from_user.id)
    await message.answer('Привет! Сейчас мы заполним небольшую анкету. Пожалуйста, ответь на несколько вопросов.',
                        reply_markup=ReplyKeyboardRemove(placeholder=False))
    await message.answer('Для начала, укажи, пожалуйста, направление, которое тебя интересует.\n(актуальные направления, которые будут набираться в этом году размещены на сайте).')
    await state.set_state(Form.direction)#устанавливаем состояние direction

@router.message(F.text == "Заполнить анкету")#обработка сообщения заполнения команды
async def button_start_form(message: types.Message, state: FSMContext):
    await cmd_form(message, state)#вызываем функцию обработки команды form 
    
    
@router.message(Form.direction)#обрабатываем "команду" direction
async def process_direction(message: types.Message, state: FSMContext): 
    if message.from_user:
        log.info("Анкета: %s выбрал направление %s", message.from_user.id, message.text)
    await state.update_data(direction=message.text)#сохраняем текст направления 
    await message.answer('Спасибо! Теперь давай перейдём к следующему шагу.')
    await message.answer('Как тебя зовут?')#отвечаем на сообщение вопросом
    await state.set_state(Form.name)#устанавливаем новое состояние 

    
@router.message(Form.name)#обрабатываем "команду"(ответ) name из формы
async def process_name(message: types.Message, state: FSMContext): 
    if message.from_user: 
        log.info("Анкета: %s ввёл имя %s", message.from_user.id, message.text)
    await state.update_data(name=message.text)#сохраняем текст имени
    await message.answer('Отлично, спасибо! Следующий вопрос.')
    await message.answer('Сколько тебе лет?')#отвечаем на сообщение с именем вопросом
    await state.set_state(Form.age)#устанавливаем состояние 
    
@router.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, введите текст.")
        return
    
    if not message.from_user:
        return 
    # проверим, что введено число
    try:
        age = int(message.text)
    except ValueError:
        log.warning("Анкета: %s ввёл некорректный возраст %s", message.from_user.id, message.text)
        await message.answer("Возраст должен быть числом, попробуйте снова:")
        return

    if not (0 < age < 130):#валидация допустимого взраста
        await message.answer("Похоже, возраст вне допустимого диапазона. Введите корректный возраст:")
        return

    log.info("Анкета: %s ввёл возраст %d", message.from_user.id, age)
    await state.update_data(age=age)

    # ⚠️ ВАЖНО: даём ЧЁТКУЮ подсказку и только затем переключаем состояние
    await message.answer("Спасибо! Почти закончили. Остались контактные данные.")
    await message.answer(PHONE_HINT)
    await state.set_state(Form.phone_number)#меняем состояние обязательно
    
@router.message(Form.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, введите номер телефона.")
        return

    if not message.from_user:
        return

    # нормализуем ввод: убираем пробелы, дефисы, скобки
    raw = message.text.strip()
    digits = re.sub(r"[^\d+]", "", raw)

    # валидация: допускаем + в начале и 10–15 цифр
    valid = PHONE_RE.fullmatch(digits) is not None

    # Дополнительная мягкая проверка на российский формат: если начинается с 8 -> в +7
    ru_like = re.sub(r"[^\d]", "", raw)
    if ru_like.startswith("8") and len(ru_like) == 11:#проверяем номер
        # преобразуем к +7##########
        digits = "+7" + ru_like[1:]
        valid = True #считаем валидным
    

    if not valid or len(raw) > 14:#если не валидный
        log.warning("Анкета: %s ввёл некорректный номер телефона %s", message.from_user.id, raw)
        await message.answer(
            "Номер телефона введён некорректно. "
            "Пожалуйста, введите номер в формате: +79991234567 или 89991234567\n"
            "Попробуйте снова:"
        )
        return

    log.info("Анкета: %s ввёл номер телефона %s", message.from_user.id, digits)
    await state.update_data(phone_number=digits)#обновляем данные 

    await message.answer(EMAIL_HINT)
    await state.set_state(Form.email)


@router.message(Form.email)
async def process_email(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, укажите email:")
        return

    email = message.text.strip()#выбираем из ответа текст
    if not EMAIL_RE.fullmatch(email):#валидируем почту
        await message.answer("Похоже, email некорректен. Введите в формате name@example.com:")
        return

    await state.update_data(email=email)#обновляем данные 
    await message.answer("Добавьте комментарий (или напишите 'нет'):")
    await state.set_state(Form.comment)
    
@router.message(Form.comment)
async def process_comment(message: types.Message, state: FSMContext):
    
    if not message.text:
        return
    #обновляем данные, если текст коммента не равен 'нет'
    await state.update_data(comment=message.text if message.text.lower() != 'нет' else None)
    
    data = await state.get_data()#получаем все сохраненные данные из состояний 
    tg_user_id = message.from_user.id if message.from_user else None

    log.info("Анкета завершена: tg_id=%s данные=%s", tg_user_id, data)#логируем завершение анкеты

    try:
        async with engine.begin() as conn:#подключаемся к базе
            await conn.execute(#исполняем
                form.insert().values(#вставка с значениями
                    tg_id=tg_user_id,
                    direction=data.get("direction"),
                    name=data.get("name"),
                    age=data.get("age"),
                    phone_number=data.get("phone_number"),
                    email=data.get("email"),
                    comment=data.get('comment'),
                )
            )
        log.info("Анкета сохранена в БД: tg_id=%s", tg_user_id)
        await message.answer(#формируем ответ
            "✅ Спасибо, анкета заполнена!\n\n"
            "📋 Вот твои данные:\n"
            f"➡️ Направление: {data.get('direction')}\n"
            f"👤 Имя: {data.get('name')}\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"📱 Телефон: {data.get('phone_number')}\n"
            f"📧 Email: {data.get('email')}\n\n"
            "Я сохранил эти данные. Можешь продолжить работу с ботом!"
        )
        await message.answer("✅ Заявка успешно сохранена! Мы свяжемся с вами.", reply_markup=main_menu)
    except Exception:#обработка исключения
        log.exception("Ошибка сохранения анкеты tg_id=%s", tg_user_id)
        await message.answer("⚠️ Не удалось сохранить анкету. Попробуйте позже.")
    finally:
        await state.clear()#очищаем состояниеx

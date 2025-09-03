from aiogram import Router, types
from app.keyboards.main_keyboard import main_menu
from app.logger import get_logger

router = Router()
logger = get_logger(__name__)

@router.message(lambda m: m.text == "ℹ️ О факультете")
async def about_faculty(message: types.Message):
    if message.from_user:
        logger.info(f"Пользователь {message.from_user.id} запросил информацию о факультете")
    await message.answer(
        "📚 Наш факультет готовит специалистов мирового уровня.\n"
        "🔹 Современные программы обучения\n"
        "🔹 Опытные преподаватели\n"
        "🔹 Возможности стажировок после первого курса",
        reply_markup=main_menu
    )

@router.message(lambda m: m.text == "📄 Документы")
async def documents(message: types.Message):
    await message.answer(
        "Для поступления нужны:\n"
        "1️⃣ Паспорт\n"
        "2️⃣ Аттестат\n"
        "3️⃣ Справка с результатами ЕГЭ\n"
        "4️⃣ Фотографии 3x4 цветные\n"
        "5️⃣ Заявление (оформляется онлайн или в приёмной комиссии)",
        reply_markup=main_menu
    )

# Обработчик для кнопки "Проходные баллы"
@router.message(lambda m: m.text == "📊 Проходные баллы")
async def scores(message: types.Message):
    await message.answer(
        "📊 Средние проходные баллы за прошлый год:\n"
        "💻 Компьютерные науки — 235\n"
        "🤖 Искусственный интеллект — 245\n"
        "🔐 Информационная безопасность — 240\n"
        "🌐 Веб-разработка — 230\n"
        "📊 Data Science — 250\n"
        "📱 Мобильная разработка — 228",
        reply_markup=main_menu
    )

# Обработчик для кнопки "Сроки подачи"
@router.message(lambda m: m.text == "📅 Сроки подачи")
async def deadlines(message: types.Message):
    await message.answer(
        "📅 Сроки приёма документов:\n"
        "🔹 Начало: 20 июня\n"
        "🔹 Конец: 20 августа\n"
        "Не опаздывайте 😉",
        reply_markup=main_menu
    )

# Обработчик для кнопки "Подать заявку"
@router.message(lambda m: m.text == "📝 Подать заявку")
async def start_form(message: types.Message):
    await message.answer("Давайте заполним анкету! ✍️\nНапишите /form, чтобы начать.", reply_markup=main_menu)


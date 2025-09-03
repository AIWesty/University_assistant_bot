from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ О факультете"), KeyboardButton(text="📄 Документы")],
        [KeyboardButton(text="📊 Проходные баллы"), KeyboardButton(text="📅 Сроки подачи")],
        [KeyboardButton(text="📝 Подать заявку"), KeyboardButton(text="💬 Оставить отзыв")],
        [KeyboardButton(text="❓ FAQ")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите нужный раздел ↓"
)
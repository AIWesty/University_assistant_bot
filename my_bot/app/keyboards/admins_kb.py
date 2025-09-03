from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_kb():#основная клава админа, после обработки  /admin
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Заявки", callback_data="admin_apps")],
        [InlineKeyboardButton(text="💬 Отзывы", callback_data="admin_feedback")],
        [InlineKeyboardButton(text="❓ FAQ (управление)", callback_data="admin_faq")],
    ])
    return kb

def form_actions_kb(app_id: int):#для работы с формами, действия
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Ответить", callback_data=f"app_reply:{app_id}")],
        [InlineKeyboardButton(text="✅ Пометить обработано", callback_data=f"app_done:{app_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"app_del:{app_id}")],
    ])

def feedback_actions_kb(feedback_id: int):#для работы с отзывами
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"fb_del:{feedback_id}")],
    ])

def faq_admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вопрос", callback_data="admin_faq_add")],#отдаем в callback дате последним элементом "действие"
        [InlineKeyboardButton(text="Посмотреть все", callback_data="admin_faq_list")],
    ])
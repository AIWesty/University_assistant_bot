from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def build_keyboard_faq(faq_list):#для формирования inline c faq на приходит выборка с вопросами из базы
    """
    faq_list = [(id, question), ...]
    Безопасно формируем inline-кнопки.
    """
    buttons = []
    for fid, q in faq_list:#проходимся по выборке, первый элемент - id вопроса, второй сам вопрос
        # убедимся, что id строка/число и callback_data не слишком длинная
        cb = f"faq_{int(fid)}"#делаем конкретную возвращаемую callback данные 
        buttons.append([InlineKeyboardButton(text=str(q), callback_data=cb)])#формируем кнопки с ней 
    return InlineKeyboardMarkup(inline_keyboard=buttons)
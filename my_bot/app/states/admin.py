from aiogram.fsm.state import StatesGroup, State

class AdminReply(StatesGroup):
    to_user = State()      # admin пишет ответ пользователю

class AdminFaq(StatesGroup):#состояния для админа с заявками и вопросами
    adding_question = State()
    adding_answer = State()
    editing_question = State()
    editing_answer = State()
    
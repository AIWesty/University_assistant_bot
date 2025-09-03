from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup): 
    direction = State() #ожидаем группу
    name = State()#ожидаем имя
    age = State()#ожидаем возраст
    phone_number = State()#номер телефона
    email = State()#ожидаем почту 
    comment = State()
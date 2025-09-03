from aiogram.fsm.state import StatesGroup, State

#описали класс состояний для задач
class AddTask(StatesGroup): 
    title = State() #состояние названия
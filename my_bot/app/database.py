from sqlalchemy import (
    MetaData, Table, Column, Integer, String, DateTime, Text, UniqueConstraint, func, CheckConstraint
)
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import config
#в этом файле "инструкция", как sqlalchemy должен подключиться к нашей postgres, создав движок, сохранив метаданные и описание таблицы, затем дать команду на создаение если она еще не создана, со всеми данными по подключению engine 


#создает "движок", используя строку подключения.
#Зачем нужно: Engine — это главный точка входа в базу данных.
engine = create_async_engine(config.ASYNC_DB_URL, echo=True)
#Этот объект будет служить каталогом или реестром, где вы зарегистрируете все таблицы вашей базы данных.
metadata = MetaData()

#обьект с описание структуры таблицы users
form = Table(
    "form",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('tg_id', Integer, nullable=False),
    Column('direction', String, nullable=False),
    Column("name", String(50), nullable=False),
    Column("age", Integer, nullable=False),
    Column('phone_number', String(14), nullable=False),
    Column("email", String, nullable=False),
    Column('comment', Text),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('status', String, server_default='new')
)

#обьект с описанием новой таблицы с задачами
tasks = Table(
    'tasks', #передаем имя таблицы
    metadata, #метаданные(инф о всех таблицах)
    Column('id', Integer, primary_key=True), #стобец айди с ключом
    Column('tg_id', Integer, nullable=False, index=True),#тг айди пользователя, индекс для быстрого поиска
    Column('title', String, nullable=False), #название задачи
    Column('status', String, nullable=False,  server_default='new'), #ее статус
    Column('created_at', DateTime(timezone=True), server_default=func.now()),#дата создания, дефолтное знаение - импортированная 
    #функция, у которой есть функция текущего времени
    CheckConstraint("status IN ('new', 'done')", name='tasks_status_check'),#ограничение проверки значений, имя - имя ограничения в бд
)

#таблица для отзывов
feedback = Table(
    'feedback',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('tg_id', Integer, nullable=False),
    Column('message', Text, nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now())#дата, по умолчанию текущее время
)

faq = Table(
    'faq',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('question', String(255), nullable=False),
    Column('answer', Text, nullable=False),
    UniqueConstraint("question", name="uq_faq_question")
)

admin_messages = Table(
    "admin_messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("admin_id", Integer, nullable=False),
    Column("user_tg_id", Integer, nullable=False),
    Column("application_id", Integer, nullable=True),
    Column("message", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)


# #Самая важная строка. Она берет все таблицы, зарегистрированные в объекте metadata, и создает их в реальной базе данных, на которую указывает engine.
# async def create_db():#обьявляем функцию создания
#     async with engine.begin() as conn:#создаем контекстный менеджер для управления соединением и транзакциями
#         await conn.run_sync(metadata.create_all)
#         #Это самая важная и хитрая строка. Она работает в два этапа.
#         #Часть 1: metadata.create_all сгенерировать SQL-команды CREATE TABLE для всех таблиц, зарегистрированных в объекте metadata.
#         #Часть 2: Это мост между асинхронным и синхронным миром. Метод асинхронного соединения (AsyncConnection).
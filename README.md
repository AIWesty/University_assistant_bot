MTI Admission Bot

Телеграм‑бот для приёмной комиссии: отвечает на FAQ, собирает заявки абитуриентов (анкета), принимает отзывы и содержит простую админ‑панель в самом Telegram.

🚀 Функциональность
	•	Главное меню: быстрые кнопки (Информация, Документы, Проходные баллы, Сроки подачи, Подать заявку, Отзыв, FAQ).
	•	FAQ: список вопросов из БД, ответы по клику на inline‑кнопки; наполнение — через скрипт и/или админку.
	•	Анкета абитуриента: имя, возраст, email, направление, телефон, комментарий → сохраняется в applications.
	•	Отзывы: любой пользователь может оставить отзыв → сохраняется в feedback.
	•	Админка (/admin):
	•	Просмотр 10 последних заявок, ответы пользователям прямо из бота, пометка «обработано», удаление.
	•	Просмотр/удаление отзывов.
	•	Управление FAQ: добавить новый вопрос/ответ.
	•	Логирование: структурированные логи с уровнем через LOG_LEVEL.
	•	Миграции: Alembic (sync‑URL), приложение — SQLAlchemy Async + asyncpg.

⸻

🧱 Технологии
	•	Python 3.13
	•	Aiogram 3.x (полностью асинхронный Telegram‑фреймворк)
	•	SQLAlchemy 2.x (async), PostgreSQL 15, asyncpg
	•	Alembic (миграции, sync‑драйвер psycopg2)
	•	Pydantic Settings (.env)
	•	Docker / Docker Compose

⸻

🗂 Структура проекта (сокращённо)

my_bot/
  bot.py                 # точка входа (polling)
  alembic.ini            # файл конфигурации миграций
  app/
    config.py            # Pydantic Settings (BOT_TOKEN, DB_URL, LOG_LEVEL, ADMIN_IDS)
    logger.py            # конфигурация логов
    database.py          # движок/сессии/metadata + таблицы (users, applications, feedback, faq)
    handlers/            # start/help/menu/form/tasks/feedback/faq/admin
    keyboards/           # main_menu, inline‑кнопки
    services/            # faq_service и др.
    states/              # FSM: анкета, админ‑состояния
  migrations/            # Alembic (env.py, версии)
  logs/
  docker/
    entrypoint.sh        # ожидание БД, миграции, запуск бота
.dockerignore
.docker-compose.yml
Dockerfile
.env.example
README.md
requirements.txt


⸻

⚙️ Переменные окружения

Создайте .env (на основе .env.example):

BOT_TOKEN=123456:ABCDEF
LOG_LEVEL=INFO

# Postgres
POSTGRES_DB=mybot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Async URL для приложения (SQLAlchemy + asyncpg)
ASYBC_DB_URL=postgresql+asyncpg://postgres:postgres@db:5432/mybot

# Sync URL для Alembic (psycopg2)
SYNC_DB_URL=postgresql+psycopg2://postgres:postgres@db:5432/mybot

# Список админов (через запятую)
ADMIN_IDS=111111111,222222222

Никогда не коммитьте настоящий .env в репозиторий. Используйте .env.example.

⸻

▶️ Локальный запуск (без Docker)
	1.	Python 3.13, виртуальное окружение, установка зависимостей:

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt


	2.	Поднимите PostgreSQL локально или в Docker и укажите DB_URL в .env.
	3.	Миграции:

alembic upgrade head


	4.	Запуск бота:

python -m my_bot.bot 



⸻

🐳 Запуск в Docker / Docker Compose
	1.	Скопируйте .env.example → .env и заполните токены/пароли.
	2.	Соберите и запустите:

docker compose build
docker compose up -d
docker compose logs -f bot

	•	Сервис db — PostgreSQL 15, данные сохраняются в volume pgdata.
	•	Сервис migrations запускает alembic upgrade head и завершается.
	•	Сервис bot зависит от migrations и стартует polling.

По умолчанию порт БД наружу не пробрасывается (безопаснее). Для локальной отладки можно добавить ports: - "5432:5432" к db.

⸻

🗃 Миграции
	•	Создать ревизию:

alembic revision --autogenerate -m "message"


	•	Применить:

alembic upgrade head


	•	Откатить:

alembic downgrade -1



Alembic использует sync‑URL (ALEMBIC_DATABASE_URL), приложение — async‑URL (DB_URL).

⸻

📚 Наполнение FAQ (демо‑данные)

python -m app.utils.load_faq_data

Скрипт аккуратно добавляет записи без дублей (или предварительно чистит таблицу в DEV‑режиме).

⸻

🔐 Админка
	•	Команда: /admin.
	•	Доступ есть только у Telegram‑ID из ADMIN_IDS.
	•	Разделы: заявки, отзывы, управление FAQ.

⸻

🧪 Тестирование (минимум)
	•	Проверьте /start, меню и /help.
	•	Пройдите анкету «Подать заявку» и удостоверьтесь, что запись появилась в БД.
	•	Откройте /admin → «Заявки» → «Ответить» — отправьте ответ самому себе из второго аккаунта/приглашённого тестера.

⸻

📦 Деплой на VPS (кратко)
	1.	Установите Docker + Docker Compose Plugin.
	2.	Склонируйте репозиторий и создайте .env.
	3.	docker compose up -d --build.
	4.	Логи: docker compose logs -f bot.
	5.	Бот на polling, поэтому дополнительных портов не требуется.

Подробная инструкция — ниже в репозитории (см. раздел «Деплой» в README).

⸻

🛡️ Безопасность
	•	Никогда не коммитьте .env.
	•	Пароли и токены храните в секретах (GitHub, CI/CD) или на сервере.
	•	Не пробрасывайте порт БД наружу, если это не нужно.

⸻

📄 Лицензия

MIT 
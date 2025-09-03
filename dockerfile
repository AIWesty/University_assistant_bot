# Dockerfile
FROM python:3.13-slim

#отключаем создание файлов .pyc и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

#установка рабочей директории
WORKDIR /app

# Системные зависимости для psycopg2/pg + удаление кеша пакетов для уменьшения образа
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
&& rm -rf /var/lib/apt/lists/*

# Зависимости копируем и устанавливаем
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# копирование всего кода
COPY . .

# Делаем entrypoint исполняемым
RUN chmod +x my_bot/docker/entrypoint.sh


# На всякий: убедимся, что пакет my_bot является модулем, создаем файл инициализации
RUN python -c "import pathlib; p = pathlib.Path('my_bot/__init__.py'); p.parent.mkdir(parents=True, exist_ok=True); p.touch()"

#запускаем скрипт-обертку вместо прямого запуска python
CMD ["my_bot/docker/entrypoint.sh"]
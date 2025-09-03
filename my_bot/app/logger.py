import os
import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import config

LOG_LEVEL = config.LOG_LEVEL.upper()#получем левл из конфига

LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'#указываем путь директории для  хранения логов, у нас это my_bot/logs будет
LOG_DIR.mkdir(parents=True, exist_ok=True)#создаем директорию по этому пути 
LOG_FILE = LOG_DIR / "app.log"#название файла куда будут писаться логи

def setup_logging() -> None: 
    """
    централизованная настройка логирования:
    - вывод в консоль (для разработки)
    - вывод в файл с ротацией (для сервера и истории)
    """
    dictConfig({
        "version": 1,#версия 1 
        "disable_existing_loggers": False,  # не глушим логеры сторонних библиотек
        "formatters": {
            "console": {#консольный формат записи логов
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
            },
            "file": {#файловый формат
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
            },
        },
        "handlers": {#обработчики логгеров
            "console": { #для консоли
                "class": "logging.StreamHandler",
                "formatter": "console",
                "level": LOG_LEVEL,
            },
            "file": {#для файла
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "file",
                "filename": str(LOG_FILE),
                "maxBytes": 1_000_000,   # 1 мб на файл
                "backupCount": 5,        # храним 5 архивов app.log.1 ... app.log.5
                "encoding": "utf-8",
                "level": LOG_LEVEL,
            },
        },
        "loggers": {
            "": {  # рут логер — всё что не переопределено ниже, то есть любые другие логи
                "handlers": ["console", "file"],
                "level": LOG_LEVEL,
            },
            # понижаем «болтливость» некоторых библиотек 
            "aiogram": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,#логи не будут описываться дважды, тк без этого лог обрабатывался и рут логером
            },
            "asyncio": {
                "handlers": ["console", "file"],
                "level": "WARNING",
                "propagate": False,
            },
        }
    })

# удобный фабричный помощник- берём именованный логер в любом модуле
def get_logger(name: str | None = None) -> logging.Logger:#мы принимаем либо name логера 
    return logging.getLogger(name if name else __name__)#либо ему присваеваем имя текущего модуля
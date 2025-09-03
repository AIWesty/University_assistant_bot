from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings): 
    BOT_TOKEN: str #указываем типы переменных
    
    ASYNC_DB_URL: str
    
    SYNC_DB_URL: str
    
    LOG_LEVEL: str = 'INFO'
    ADMIN_IDS: str = ''
    
    model_config = SettingsConfigDict(
        case_sensitive=False    # имена переменных строго большие буквы
    )
    @property
    def admin_ids(self) -> list[int]:
        # возвращает список int, безопасно
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

config = Settings() # type: ignore
    
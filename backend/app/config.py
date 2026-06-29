from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "VoxForge"
    SECRET_KEY: str = "voxforge-dev-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./data/db/voxforge.db"
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://localhost:5180"]
    UPLOAD_DIR: str = "./data/uploads"
    OUTPUT_DIR: str = "./data/outputs"
    CLONE_DIR: str = "./data/cloned_voices"
    PREVIEW_DIR: str = "./data/previews"
    TEMP_CHUNK_DIR: str = "./data/temp_chunks"
    LONG_FORM_DIR: str = "./data/outputs/long_form"
    MAX_TEXT_LENGTH: int = 5000
    LONG_FORM_MAX_CHARS: int = 30000
    LONG_FORM_CHUNK_SIZE: int = 1500
    DEFAULT_CHAR_QUOTA: int = 50000
    MAX_UPLOAD_SIZE: int = 52428800
    ALLOWED_AUDIO_EXTENSIONS: list = [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".webm"]
    ADMIN_GATE_PASSWORD_HASH: str = ""

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()

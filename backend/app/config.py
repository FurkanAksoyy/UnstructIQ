from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # API Keys
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # App Settings
    APP_NAME: str = "UnstructIQ"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # File Upload Settings
    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"
    MAX_FILE_SIZE: int = 50000000  # 50MB
    ALLOWED_EXTENSIONS: str = ".csv,.json,.xlsx,.xls,.txt,.pdf"  # String olarak

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_allowed_extensions(self):
        """Returns list of allowed extensions"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]


# Singleton instance
settings = Settings()

# Klasörlerin varlığını kontrol et ve oluştur
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
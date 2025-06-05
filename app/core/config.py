from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # API settings
    API_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "LingvalexaEducation"
    DEBUG: bool = False
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # BunnyCDN settings
    BUNNYCDN_API_KEY: str
    BUNNYCDN_STORAGE_ZONE: str = ''
    BUNNYCDN_PULL_ZONE: str = ''
    
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PORT: int = 8000

    @field_validator("SUPABASE_URL", "SUPABASE_KEY", "BUNNYCDN_API_KEY", mode="before")
    @classmethod
    def check_required_fields(cls, v, info):
        if not v or str(v).strip() == "":
            print(f"Validation error for field: {info.field_name}, value: {v}") 
            raise ValueError(f"{info.field_name} is a required configuration field and cannot be empty")
        return v

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"

try:
    _settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    raise

def validate_settings() -> Settings:
    """
    Validates that all required settings are present and not empty.
    Raises ValueError if any critical setting is missing.
    """
    critical_settings = [
        "SUPABASE_URL", "SUPABASE_KEY", "BUNNYCDN_API_KEY"
    ]
    
    for setting in critical_settings:
        value = getattr(_settings, setting, None)
        if not value or str(value).strip() == "":
            raise ValueError(f"Critical setting {setting} is missing or empty")
    
    return _settings

# Expose settings object only after validation
settings = validate_settings()

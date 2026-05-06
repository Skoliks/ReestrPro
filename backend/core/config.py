from pydantic_settings import BaseSettings, SettingsConfigDict
#DATABASE_URL=postgresql+psycopg2://postgres:forgive12@localhost:5432/for_construction_company

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
settings = Settings()
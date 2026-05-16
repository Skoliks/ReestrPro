from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str
    
    debug: bool = False
    
    gigachat_credentials: str | None = None
    gigachat_model: str = "GigaChat"
    gigachat_verify_ssl_certs: bool = False
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
settings = Settings()
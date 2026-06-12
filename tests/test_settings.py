import pytest
from pydantic import ValidationError

from backend.core.config import Settings


def test_settings_load_required_database_variables(monkeypatch):
    monkeypatch.setenv("DB_USER", "user")
    monkeypatch.setenv("DB_PASSWORD", "password")
    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "reestr")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:4173")

    settings = Settings(_env_file=None)

    assert settings.db_user == "user"
    assert settings.db_password == "password"
    assert settings.db_host == "db"
    assert settings.db_port == 5433
    assert settings.db_name == "reestr"
    assert settings.database_url == "postgresql://user:password@db:5433/reestr"
    assert settings.async_database_url == "postgresql+asyncpg://user:password@db:5433/reestr"
    assert settings.cors_allowed_origins == [
        "http://localhost:5173",
        "http://localhost:4173",
    ]


def test_settings_raise_clear_error_without_required_database_variables(monkeypatch):
    for env_name in ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]:
        monkeypatch.delenv(env_name, raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    error_fields = {tuple(error["loc"]) for error in exc_info.value.errors()}

    assert ("db_user",) in error_fields
    assert ("db_password",) in error_fields
    assert ("db_name",) in error_fields

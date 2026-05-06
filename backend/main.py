from fastapi import FastAPI

from backend.core.logging import setup_logger, get_logger
from backend.core.config import settings
from backend.api.health import router as health_router

setup_logger()
get_logger(__name__)

app = FastAPI(
    title="РеестрПро", 
    description="Приложение для поиска сертификатов и деклараций соответствия",
    version="Alpha",
    debug=settings.debug
)

app.include_router(health_router)
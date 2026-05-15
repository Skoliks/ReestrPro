from fastapi import FastAPI

from backend.core.logging import setup_logger, get_logger
from backend.core.config import settings
from backend.api.documents import router as documents_router
from backend.api.health import router as health_router
from backend.api.search import router as search_router
from backend.api.semantic_search import router as semantic_search_router
from backend.api.hybrid_search import router as hybrid_search_router

setup_logger()
get_logger(__name__)

app = FastAPI(
    title="РеестрПро", 
    description="Приложение для поиска сертификатов и деклараций соответствия",
    version="Alpha",
    debug=settings.debug
)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(semantic_search_router)
app.include_router(hybrid_search_router)
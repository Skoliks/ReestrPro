from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.documents import router as documents_router
from backend.api.health import router as health_router
from backend.api.hybrid_search import router as hybrid_search_router
from backend.api.rag import router as rag_router
from backend.api.search import router as search_router
from backend.api.semantic_search import router as semantic_search_router
from backend.core.config import settings
from backend.core.logging import get_logger, setup_logger

setup_logger()
get_logger(__name__)

app = FastAPI(
    title="РеестрПро",
    description="Приложение для поиска сертификатов и деклараций соответствия",
    version="Alpha",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(semantic_search_router)
app.include_router(hybrid_search_router)
app.include_router(rag_router)

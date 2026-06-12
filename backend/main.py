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
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Backend service for registry document search and RAG answers",
    version="Alpha",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
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


@app.on_event("startup")
def log_application_startup() -> None:
    logger.info(
        "Application started: debug=%s cors_origins=%s",
        settings.debug,
        settings.cors_allowed_origins,
    )

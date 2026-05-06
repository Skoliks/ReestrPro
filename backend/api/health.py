from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.db.session import get_db
from backend.core.logging import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/health", tags=["verification"])

@router.get("")
def health():
    logger.info("the application is working")
    return {"status": "ok"}


@router.get("/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        logger.info("database connected")
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        logger.error("Database health check failed",exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "database": "disconnected"
                }
)
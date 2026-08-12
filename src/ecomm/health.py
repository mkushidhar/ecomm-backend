import time
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ecomm.database import get_db

router = APIRouter(prefix="/api/v1")
DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/health")
async def health(db: DbSession) -> dict[str, str | dict[str, str | float]]:

    db_status = "ok"
    start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    return {
        "api": "running",
        "database": {
            "status": db_status,
            "latency_ms": latency_ms,
        },
    }

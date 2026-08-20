import time

from fastapi import APIRouter
from sqlalchemy import text

from ecomm.core.database import DbConn

router = APIRouter(
    prefix="/api/v1",
    tags=["Health"],
)


@router.get("/health")
async def health(db: DbConn) -> dict[str, str | dict[str, str | float]]:

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

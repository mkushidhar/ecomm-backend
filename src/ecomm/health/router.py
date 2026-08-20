import time

from fastapi import APIRouter, status
from sqlalchemy import text

from ecomm.core.database import DbConn

from .schemas import DBStatus, ReturnHealth

router = APIRouter(
    prefix="/api/v1",
    tags=["Health"],
)


async def check_database(db: DbConn) -> DBStatus:
    start = time.perf_counter()

    latency_ms = round(
        (time.perf_counter() - start) * 1000,
        2,
    )

    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        return DBStatus(
            status="unreachable",
            latency_ms=latency_ms,
        )

    return DBStatus(
        status="ok",
        latency_ms=latency_ms,
    )


@router.get(
    "/health",
    response_model=ReturnHealth,
    status_code=status.HTTP_200_OK,
)
async def health(db: DbConn) -> ReturnHealth:
    database = await check_database(db)

    return ReturnHealth(
        api="running",
        database=database,
    )

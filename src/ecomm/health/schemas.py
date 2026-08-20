from typing import Literal

from pydantic import BaseModel


class ReturnHealth(BaseModel):
    api: str
    database: DBStatus


class DBStatus(BaseModel):
    status: Literal["ok", "unreachable"]
    latency_ms: float | None

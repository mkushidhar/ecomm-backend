from fastapi import FastAPI

from ecomm.health import router as health_router
from ecomm.products import product_router

app = FastAPI(title="e-comm")

app.include_router(health_router)
app.include_router(product_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "working"}

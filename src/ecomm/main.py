from fastapi import FastAPI

app = FastAPI(title="e-comm")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "working"}

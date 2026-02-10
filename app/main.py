from fastapi import FastAPI
from app.api.routes.reports import reports_router

app = FastAPI(
    title="Veterinary Reports API",
    version="1.0.0",
)

app.include_router(reports_router)


@app.get("/health")
def health():
    return {"status": "ok"}

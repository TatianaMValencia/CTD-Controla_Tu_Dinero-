from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

# DB se crea vía Alembic (entrypoint: alembic upgrade head). No create_all aquí.

app = FastAPI(title="PWA Finanzas Personales API", version="1.0.0-mvp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/health")
def health_v1():
    from sqlalchemy import text

    from app.core.database import engine

    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        return {"db": "error", "detail": str(e)[:200]}


app.include_router(api_router, prefix="/api/v1")

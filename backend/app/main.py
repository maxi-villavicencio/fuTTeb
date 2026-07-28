"""Punto de entrada de la API (FastAPI).

Crea la aplicación y registra los routers. La API expone endpoints y delega
toda la inteligencia en el engine; aquí no se calcula el Índice de Apuesta.

Levantar en local (con el .venv activado y las dependencias instaladas):

    uvicorn backend.app.main:app --reload

Luego probar: http://127.0.0.1:8000/health
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import analyze, health, teams

app = FastAPI(
    title=settings.APP_NAME,
    description="API de Bet Analyzer AI. Expone el engine de análisis de apuestas.",
    version="0.1.0",
)

# CORS: permitir que el frontend (Next.js en desarrollo) llame a la API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(teams.router)
app.include_router(analyze.router)


@app.get("/")
def root() -> dict:
    """Raíz informativa de la API."""
    return {
        "service": settings.APP_NAME,
        "docs": "/docs",
        "health": "/health",
        "teams": "/teams",
        "analyze": "/analyze (POST)",
    }

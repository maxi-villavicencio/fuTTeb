"""Endpoint de salud.

``GET /health`` -> comprueba que la API está viva. No toca el engine ni la
base de datos; sirve como sonda básica de disponibilidad.
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Devuelve el estado de la API."""
    return {"status": "ok", "service": "Bet Analyzer AI API"}

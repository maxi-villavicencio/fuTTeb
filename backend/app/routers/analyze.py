"""Endpoint de análisis (placeholder).

``POST /analyze`` -> en el diseño final, la API delega en el engine para
obtener el Índice de Apuesta de un mercado y solo devuelve el resultado.

De momento es un MOCK: no calcula nada (la API nunca calcula) y no llama al
engine todavía. Solo demuestra el contrato de entrada/salida.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["analyze"])


class AnalyzeRequest(BaseModel):
    """Entrada del análisis (esbozo)."""

    home_team: str
    away_team: str
    market: str  # p. ej. "goals", "corners", "cards", "shots", "btts"


@router.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    """Devuelve un resultado MOCK con la forma esperada del engine.

    En el futuro, aquí se llamará al engine:
        resultado = engine.core.registry.get_market(request.market).calculate(ctx)
    y se devolverá ``resultado`` tal cual. La API no calcula.
    """
    return {
        "market": request.market,
        "match": f"{request.home_team} vs {request.away_team}",
        "bet_index": None,  # mock: el engine lo calculará
        "probabilities": {},  # mock
        "explanation": "Respuesta de ejemplo (mock). El engine aún no está conectado.",
        "mock": True,
    }

"""Modelos Pydantic de la API (request/response).

Tipado claro de lo que entra y sale de la API. La API NO calcula: estos modelos
solo dan forma a lo que el engine devuelve, para que el frontend lo consuma
fácil y de manera consistente entre mercados.
"""

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------
# Equipos
# --------------------------------------------------------------------------
class TeamOut(BaseModel):
    """Equipo para desplegables y para identificar local/visitante."""

    id: int
    name: str
    short_name: str | None = None


class TeamsResponse(BaseModel):
    """Respuesta de GET /teams."""

    equipos: list[TeamOut]


# --------------------------------------------------------------------------
# Análisis
# --------------------------------------------------------------------------
class AnalyzeRequest(BaseModel):
    """Body de POST /analyze: los dos equipos a analizar."""

    home_team_id: int = Field(..., description="Id del equipo local.")
    away_team_id: int = Field(..., description="Id del equipo visitante.")


class MarketResponse(BaseModel):
    """Resultado de un mercado, con envoltura CONSISTENTE entre mercados.

    Campos comunes a todos los mercados:
        market:       código del mercado ("corners", "goals", "cards", "btts").
        indice:       índice de apuesta 0-100 (interpretación propia de cada mercado).
        confiable:    si hay datos históricos suficientes.
        advertencias: avisos (p. ej. datos insuficientes); vacío si todo OK.
        explicacion:  texto en español que justifica el resultado.
        valores:      detalle específico del mercado, ya estructurado por el engine
                      (para goles: over_under, btts, marcadores_top, rangos_top;
                       para tarjetas: mercados_total/local/visitante; etc.).
    """

    market: str
    indice: float
    confiable: bool
    advertencias: list[str] = []
    explicacion: str
    valores: dict


class AnalyzeResponse(BaseModel):
    """Respuesta de POST /analyze: los 4 mercados para el par de equipos."""

    partido: str
    home_team: TeamOut
    away_team: TeamOut
    corners: MarketResponse
    goals: MarketResponse
    cards: MarketResponse
    btts: MarketResponse

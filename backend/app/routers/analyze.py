"""Endpoint de análisis.

``POST /analyze`` -> recibe dos equipos y devuelve los 4 mercados calculados por
el engine (corners, goles, tarjetas, btts). La API NO calcula: delega en el
servicio, que delega en el engine, y solo da forma HTTP al resultado.

Notas de errores:
  - equipos iguales      -> 400 (Bad Request)
  - equipo inexistente   -> 404 (Not Found)
  - datos insuficientes  -> NO es error: se devuelve 200 con confiable=False y
                            las advertencias correspondientes (lo decide el engine).
"""

from fastapi import APIRouter, HTTPException

from engine.core.types import MarketResult

from ..schemas import AnalyzeRequest, AnalyzeResponse, MarketResponse, TeamOut
from ..services import analysis_service
from ..services.analysis_service import EquipoInexistenteError, MismoEquipoError

router = APIRouter(tags=["analyze"])


def _a_market_response(resultado: MarketResult) -> MarketResponse:
    """Convierte un MarketResult del engine en el modelo de respuesta de la API."""
    return MarketResponse(
        market=resultado.market,
        indice=resultado.indice,
        confiable=resultado.confiable,
        advertencias=resultado.advertencias,
        explicacion=resultado.explicacion,
        valores=resultado.valores,
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analiza un partido (local vs visitante) y devuelve los 4 mercados."""
    try:
        datos = analysis_service.analizar_partido(
            request.home_team_id, request.away_team_id
        )
    except MismoEquipoError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except EquipoInexistenteError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # error inesperado del engine o de la base
        raise HTTPException(
            status_code=500,
            detail=f"Error al calcular el análisis: {exc}",
        ) from exc

    home = TeamOut(**datos["home"])
    away = TeamOut(**datos["away"])

    return AnalyzeResponse(
        partido=f"{home.name} vs {away.name}",
        home_team=home,
        away_team=away,
        corners=_a_market_response(datos["corners"]),
        goals=_a_market_response(datos["goals"]),
        cards=_a_market_response(datos["cards"]),
        btts=_a_market_response(datos["btts"]),
    )

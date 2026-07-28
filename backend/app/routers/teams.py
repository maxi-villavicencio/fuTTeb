"""Endpoint de equipos.

``GET /teams`` -> lista de equipos (id y nombre) para poblar los desplegables
de local y visitante en la web. Solo lee de la base vía el servicio; no calcula.
"""

from fastapi import APIRouter, HTTPException

from ..schemas import TeamsResponse
from ..services import analysis_service

router = APIRouter(tags=["teams"])


@router.get("/teams", response_model=TeamsResponse)
def get_teams() -> TeamsResponse:
    """Devuelve los equipos disponibles, ordenados por nombre."""
    try:
        equipos = analysis_service.listar_equipos()
    except Exception as exc:  # p. ej. base de datos caída
        raise HTTPException(
            status_code=503,
            detail=f"No se pudieron obtener los equipos: {exc}",
        ) from exc
    return TeamsResponse(equipos=equipos)

"""Servicio de análisis: puente entre la API y el engine.

Es el ÚNICO lugar del backend que conoce los plugins del engine. La API llama
a este servicio; el servicio llama al engine y devuelve sus resultados. La API
sigue sin calcular nada.

Dirección de dependencia: backend -> engine (nunca al revés).
"""

from engine.core.types import MarketResult
from engine.data import statistics_repository as repo
from engine.markets.btts import calcular as calcular_btts
from engine.markets.cards import calcular as calcular_cards
from engine.markets.corners import calcular as calcular_corners
from engine.markets.goals import calcular as calcular_goals


class EquipoInexistenteError(Exception):
    """Se pidió analizar un equipo cuyo id no existe en la base."""

    def __init__(self, team_id: int):
        self.team_id = team_id
        super().__init__(f"No existe un equipo con id {team_id}.")


class MismoEquipoError(Exception):
    """Se pidió analizar un equipo contra sí mismo."""

    def __init__(self):
        super().__init__("El equipo local y el visitante no pueden ser el mismo.")


def listar_equipos() -> list[dict]:
    """Devuelve los equipos disponibles (id, name, short_name), ordenados por nombre."""
    return repo.listar_equipos()


def analizar_partido(home_team_id: int, away_team_id: int) -> dict:
    """Valida los equipos y calcula los 4 mercados llamando al engine.

    Returns:
        dict con: home (dict), away (dict) y los MarketResult de cada mercado
        bajo las claves 'corners', 'goals', 'cards', 'btts'.

    Raises:
        MismoEquipoError:      si ambos ids son iguales.
        EquipoInexistenteError: si alguno de los equipos no existe.
    """
    if home_team_id == away_team_id:
        raise MismoEquipoError()

    home = repo.equipo_por_id(home_team_id)
    if home is None:
        raise EquipoInexistenteError(home_team_id)

    away = repo.equipo_por_id(away_team_id)
    if away is None:
        raise EquipoInexistenteError(away_team_id)

    # La API NO calcula: toda la inteligencia es del engine.
    resultados: dict[str, MarketResult] = {
        "corners": calcular_corners(home_team_id, away_team_id),
        "goals": calcular_goals(home_team_id, away_team_id),
        "cards": calcular_cards(home_team_id, away_team_id),
        "btts": calcular_btts(home_team_id, away_team_id),
    }

    return {"home": home, "away": away, **resultados}

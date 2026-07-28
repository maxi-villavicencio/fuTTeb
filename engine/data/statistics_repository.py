"""Repositorio de lectura de estadísticas crudas (MatchStatistics).

Encapsula TODO el SQL de acceso a la tabla ``MatchStatistics``. Los mercados
(calculators) usan estas funciones y NUNCA escriben SQL suelto.

Recordar el formato de la tabla: una fila por equipo por partido, con
``is_home`` (1 = jugó de local, 0 = de visitante) y ``opponent_team_id`` para
poder mirar la fila del rival en el mismo partido.

Convención de "genera" vs "concede":
    - córners que un equipo GENERA  -> su propia columna ``corners``.
    - córners que un equipo CONCEDE -> los córners del rival en ese partido
      (se obtiene uniendo la fila del equipo con la del oponente por match_id).
"""

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.engine import Engine

from engine.data.connection import get_engine


@dataclass
class PromedioMuestra:
    """Promedio de una métrica junto al tamaño de la muestra que lo respalda.

    Atributos:
        promedio: media de la métrica (0.0 si no hay datos).
        partidos: cantidad de partidos considerados (0 si no hay datos).
    """

    promedio: float
    partidos: int

    @property
    def hay_datos(self) -> bool:
        return self.partidos > 0


def _ejecutar_promedio(sql: str, params: dict, engine: Engine | None) -> PromedioMuestra:
    """Ejecuta una consulta que devuelve (promedio, n) y la envuelve."""
    engine = engine or get_engine()
    with engine.connect() as conn:
        fila = conn.execute(text(sql), params).one()
    promedio = float(fila.promedio) if fila.promedio is not None else 0.0
    partidos = int(fila.n) if fila.n is not None else 0
    return PromedioMuestra(promedio=promedio, partidos=partidos)


def corners_generados(team_id: int, de_local: bool, engine: Engine | None = None) -> PromedioMuestra:
    """Promedio de córners que un equipo GENERA, filtrando por localía.

    Args:
        team_id:  equipo a analizar.
        de_local: True -> solo partidos donde jugó de local (is_home=1);
                  False -> solo de visitante (is_home=0).
    """
    sql = """
        SELECT AVG(CAST(corners AS FLOAT)) AS promedio,
               COUNT(corners)              AS n
        FROM dbo.MatchStatistics
        WHERE team_id = :tid
          AND is_home = :ish
          AND corners IS NOT NULL
    """
    return _ejecutar_promedio(sql, {"tid": team_id, "ish": 1 if de_local else 0}, engine)


def corners_concedidos(team_id: int, de_local: bool, engine: Engine | None = None) -> PromedioMuestra:
    """Promedio de córners que un equipo CONCEDE (córners del rival), por localía.

    Se une la fila del equipo con la de su oponente en el mismo partido.

    Args:
        team_id:  equipo a analizar.
        de_local: True -> partidos donde el equipo jugó de local (is_home=1);
                  False -> de visitante (is_home=0).
    """
    sql = """
        SELECT AVG(CAST(opp.corners AS FLOAT)) AS promedio,
               COUNT(opp.corners)              AS n
        FROM dbo.MatchStatistics t
        JOIN dbo.MatchStatistics opp
          ON opp.match_id = t.match_id
         AND opp.team_id  = t.opponent_team_id
        WHERE t.team_id = :tid
          AND t.is_home = :ish
          AND opp.corners IS NOT NULL
    """
    return _ejecutar_promedio(sql, {"tid": team_id, "ish": 1 if de_local else 0}, engine)


# --------------------------------------------------------------------------
# Goles (usados por el mercado de Goles)
# --------------------------------------------------------------------------

def goles_marcados(team_id: int, de_local: bool, engine: Engine | None = None) -> PromedioMuestra:
    """Promedio de goles que un equipo MARCA, filtrando por localía.

    Args:
        team_id:  equipo a analizar.
        de_local: True -> partidos de local (is_home=1); False -> de visitante.
    """
    sql = """
        SELECT AVG(CAST(goals AS FLOAT)) AS promedio,
               COUNT(goals)              AS n
        FROM dbo.MatchStatistics
        WHERE team_id = :tid
          AND is_home = :ish
          AND goals IS NOT NULL
    """
    return _ejecutar_promedio(sql, {"tid": team_id, "ish": 1 if de_local else 0}, engine)


def goles_concedidos(team_id: int, de_local: bool, engine: Engine | None = None) -> PromedioMuestra:
    """Promedio de goles que un equipo CONCEDE, filtrando por localía.

    Usa la columna cruda ``goals_conceded`` de MatchStatistics (no necesita
    unir con la fila del rival).

    Args:
        team_id:  equipo a analizar.
        de_local: True -> partidos de local (is_home=1); False -> de visitante.
    """
    sql = """
        SELECT AVG(CAST(goals_conceded AS FLOAT)) AS promedio,
               COUNT(goals_conceded)              AS n
        FROM dbo.MatchStatistics
        WHERE team_id = :tid
          AND is_home = :ish
          AND goals_conceded IS NOT NULL
    """
    return _ejecutar_promedio(sql, {"tid": team_id, "ish": 1 if de_local else 0}, engine)


# --------------------------------------------------------------------------
# Ayudantes de catálogo (para pruebas y para mostrar nombres en explicaciones)
# --------------------------------------------------------------------------

def nombre_equipo(team_id: int, engine: Engine | None = None) -> str:
    """Devuelve el nombre corto del equipo (o 'Equipo <id>' si no se encuentra)."""
    engine = engine or get_engine()
    with engine.connect() as conn:
        fila = conn.execute(
            text("SELECT short_name FROM dbo.Teams WHERE id = :tid"),
            {"tid": team_id},
        ).first()
    return fila.short_name if fila and fila.short_name else f"Equipo {team_id}"


def id_por_nombre_corto(nombre: str, engine: Engine | None = None) -> int | None:
    """Devuelve el id del equipo cuyo short_name coincide (o None)."""
    engine = engine or get_engine()
    with engine.connect() as conn:
        fila = conn.execute(
            text("SELECT id FROM dbo.Teams WHERE short_name = :n"),
            {"n": nombre},
        ).first()
    return int(fila.id) if fila else None

"""Reglas y validaciones del mercado: Tarjetas.

Mismo criterio de confiabilidad que córners, goles y btts: el índice es
CONFIABLE solo si el LOCAL tiene al menos MIN_PARTIDOS_CONFIABLE partidos DE
LOCAL y el VISITANTE al menos MIN_PARTIDOS_CONFIABLE partidos DE VISITANTE.

Si no se cumple, NO rompe ni cambia el cálculo: marca confiable=False y devuelve
una advertencia detallada.
"""

from .weights import MIN_PARTIDOS_CONFIABLE


def validar_confiabilidad(
    nombre_local: str,
    partidos_local: int,
    nombre_visitante: str,
    partidos_visitante: int,
) -> tuple[list[str], bool]:
    """Aplica el umbral de confiabilidad a los partidos de cada equipo."""
    advertencias: list[str] = []
    confiable = True

    if partidos_local < MIN_PARTIDOS_CONFIABLE:
        advertencias.append(
            f"{nombre_local} solo tiene {partidos_local} partidos de local; "
            f"se requieren {MIN_PARTIDOS_CONFIABLE} para un índice confiable."
        )
        confiable = False

    if partidos_visitante < MIN_PARTIDOS_CONFIABLE:
        advertencias.append(
            f"{nombre_visitante} solo tiene {partidos_visitante} partidos de visitante; "
            f"se requieren {MIN_PARTIDOS_CONFIABLE} para un índice confiable."
        )
        confiable = False

    return advertencias, confiable

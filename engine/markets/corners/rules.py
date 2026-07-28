"""Reglas y validaciones del mercado: Córners.

Decide si el índice es CONFIABLE según la cantidad de partidos históricos del
tipo relevante:
    - el LOCAL necesita al menos MIN_PARTIDOS_CONFIABLE partidos DE LOCAL;
    - el VISITANTE necesita al menos MIN_PARTIDOS_CONFIABLE partidos DE VISITANTE.

Si no se cumple, NO rompe ni cambia el cálculo: solo marca confiable=False y
devuelve una advertencia que dice cuántos partidos tiene cada equipo.
"""

from .weights import MIN_PARTIDOS_CONFIABLE


def validar_confiabilidad(
    nombre_local: str,
    partidos_local: int,
    nombre_visitante: str,
    partidos_visitante: int,
) -> tuple[list[str], bool]:
    """Aplica el umbral de confiabilidad a los partidos de cada equipo.

    Args:
        nombre_local:       nombre del equipo local (para el mensaje).
        partidos_local:     cantidad de partidos DE LOCAL del equipo local.
        nombre_visitante:   nombre del equipo visitante (para el mensaje).
        partidos_visitante: cantidad de partidos DE VISITANTE del visitante.

    Returns:
        (advertencias, confiable):
            advertencias: lista de mensajes en español (vacía si todo OK).
            confiable:    False si algún equipo no llega al umbral.
    """
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

"""Generador de explicaciones del mercado: Córners.

Construye la explicación legible (en español) que justifica el índice. Recibe
los números ya calculados y arma un texto transparente; NO calcula nada.
La web solo muestra este texto.
"""

from . import weights


def generar_explicacion(datos: dict) -> str:
    """Arma la explicación en español a partir del dict de valores del cálculo.

    ``datos`` es el mismo dict que viaja en ``MarketResult.valores`` e incluye
    nombres de equipos, promedios por componente y los esperados/índice finales.
    """
    n_local = datos["nombre_local"]
    n_visita = datos["nombre_visitante"]

    lineas = [
        f"Córners — {n_local} (local) vs {n_visita} (visitante):",
        "",
        f"• {n_local} genera {datos['local_genera']:.1f} córners de local "
        f"({datos['local_genera_n']} part.).",
        f"• {n_visita} concede {datos['visitante_concede']:.1f} córners de visitante "
        f"({datos['visitante_concede_n']} part.).",
        f"   → Esperados del local: {datos['esperados_local']:.1f}",
        "",
        f"• {n_visita} genera {datos['visitante_genera']:.1f} córners de visitante "
        f"({datos['visitante_genera_n']} part.).",
        f"• {n_local} concede {datos['local_concede']:.1f} córners de local "
        f"({datos['local_concede_n']} part.).",
        f"   → Esperados del visitante: {datos['esperados_visitante']:.1f}",
        "",
        f"Total esperado: {datos['corners_totales']:.1f} córners "
        f"(línea {weights.LINEA_CORNERS}).",
    ]

    # Interpretación del índice respecto de la línea.
    diferencia = datos["corners_totales"] - weights.LINEA_CORNERS
    if diferencia > 0:
        interpretacion = (
            f"Se esperan ~{diferencia:.1f} córners POR ENCIMA de la línea, "
            "por eso el índice es alto."
        )
    elif diferencia < 0:
        interpretacion = (
            f"Se esperan ~{abs(diferencia):.1f} córners POR DEBAJO de la línea, "
            "por eso el índice es bajo."
        )
    else:
        interpretacion = "Los córners esperados caen justo sobre la línea (índice neutral)."

    lineas.append(f"Índice: {datos['indice']:.0f}/100 — {interpretacion}")

    # Ponderación usada (transparencia).
    lineas.append(
        f"(Ponderación genera/concede: "
        f"{weights.PESO_GENERA:.0%}/{weights.PESO_CONCEDE:.0%}.)"
    )

    return "\n".join(lineas)

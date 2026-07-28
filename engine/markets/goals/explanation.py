"""Generador de explicaciones del mercado: Goles.

Construye la explicación legible (en español) a partir de los números ya
calculados. NO calcula nada. La web solo muestra este texto.
"""

from . import weights


def generar_explicacion(datos: dict) -> str:
    """Arma la explicación en español a partir del dict de valores del cálculo."""
    n_local = datos["nombre_local"]
    n_visita = datos["nombre_visitante"]
    ou = datos["over_under"]
    btts = datos["btts"]

    # Top de marcadores y de rangos, formateados como "etiqueta: %".
    marcadores_txt = ", ".join(
        f"{m['texto']}: {m['prob']:.1%}" for m in datos["marcadores_top"]
    )
    rangos_txt = ", ".join(
        f"{r['rango']}: {r['prob']:.1%}" for r in datos["rangos_top"]
    )

    lineas = [
        f"Goles — {n_local} (local) vs {n_visita} (visitante):",
        "",
        "Goles esperados (ponderación 60% ataque / 40% defensa del rival):",
        f"• {n_local}: {datos['goles_esperados_local']:.2f}  "
        f"(marca {datos['local_marca']:.2f} de local, {datos['local_marca_n']} part.; "
        f"{n_visita} concede {datos['visitante_concede']:.2f} de visitante, "
        f"{datos['visitante_concede_n']} part.).",
        f"• {n_visita}: {datos['goles_esperados_visitante']:.2f}  "
        f"(marca {datos['visitante_marca']:.2f} de visitante, {datos['visitante_marca_n']} part.; "
        f"{n_local} concede {datos['local_concede']:.2f} de local, "
        f"{datos['local_concede_n']} part.).",
        f"Total esperado: {datos['goles_esperados_total']:.2f} goles.",
        "",
        "Mercados (derivados de la matriz de Poisson):",
        f"• Over/Under {ou['linea']}: probabilidad de Over {ou['prob_over']:.0%} "
        f"→ índice {ou['indice']:.0f}/100.",
        f"• Ambos marcan (BTTS): {btts['prob_si']:.0%} "
        f"→ índice {btts['indice']:.0f}/100.",
        f"• Marcadores más probables: {marcadores_txt}.",
        f"• Rangos de goles más probables (ancho {datos['ancho_rango']}): {rangos_txt}.",
        "",
        f"(Máximo de la matriz: {weights.MAX_GOLES_MATRIZ} goles por equipo; "
        "el último casillero acumula la cola para que sume 100%.)",
    ]

    return "\n".join(lineas)

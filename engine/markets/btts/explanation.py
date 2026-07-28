"""Generador de explicaciones del mercado: Ambos equipos marcan (BTTS).

Construye la explicación legible (en español) a partir de los números ya
calculados. NO calcula nada. La web solo muestra este texto.
"""


def _cualitativo(prob: float) -> str:
    """Traduce una probabilidad a un adjetivo legible."""
    if prob >= 0.70:
        return "muy probable"
    if prob >= 0.55:
        return "probable"
    if prob >= 0.45:
        return "parejo"
    if prob >= 0.30:
        return "poco probable"
    return "muy poco probable"


def generar_explicacion(datos: dict) -> str:
    """Arma la explicación en español a partir del dict de valores del cálculo."""
    n_local = datos["nombre_local"]
    n_visita = datos["nombre_visitante"]
    p_local = datos["prob_local_marca"]
    p_visita = datos["prob_visitante_marca"]

    lineas = [
        f"BTTS (ambos marcan) — {n_local} (local) vs {n_visita} (visitante):",
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
        "",
        f"• {n_local} marca al menos 1: {p_local:.0%} ({_cualitativo(p_local)}).",
        f"• {n_visita} marca al menos 1: {p_visita:.0%} ({_cualitativo(p_visita)}).",
        f"→ Que AMBOS marquen = {p_local:.0%} × {p_visita:.0%} = "
        f"{datos['prob_si']:.0%}.",
        "",
        f"BTTS: Sí {datos['prob_si']:.0%} / No {datos['prob_no']:.0%}  "
        f"→ índice {datos['indice']:.0f}/100.",
    ]

    return "\n".join(lineas)

"""Generador de explicaciones del mercado: Tarjetas.

Construye la explicación legible (en español) a partir de los números ya
calculados. NO calcula nada. La web solo muestra este texto.
"""


def _formatear_mercados(mercados: list[dict]) -> str:
    """Convierte una lista de mercados de línea en texto: 'línea (desc): %'."""
    return ", ".join(
        f"{m['linea']} ({m['descripcion']}): {m['prob']:.1%}" for m in mercados
    )


def generar_explicacion(datos: dict) -> str:
    """Arma la explicación en español a partir del dict de valores del cálculo."""
    n_local = datos["nombre_local"]
    n_visita = datos["nombre_visitante"]

    lineas_txt = [
        f"Tarjetas — {n_local} (local) vs {n_visita} (visitante):",
        "",
        "Tarjetas esperadas (amarilla o roja = 1; ponderación 60% propias / "
        "40% las que provoca el rival):",
        f"• {n_local}: {datos['tarjetas_esperadas_local']:.2f}  "
        f"(recibe {datos['local_genera']:.2f} de local, {datos['local_genera_n']} part.; "
        f"{n_visita} provoca {datos['visitante_provoca']:.2f} de visitante, "
        f"{datos['visitante_provoca_n']} part.).",
        f"• {n_visita}: {datos['tarjetas_esperadas_visitante']:.2f}  "
        f"(recibe {datos['visitante_genera']:.2f} de visitante, {datos['visitante_genera_n']} part.; "
        f"{n_local} provoca {datos['local_provoca']:.2f} de local, "
        f"{datos['local_provoca_n']} part.).",
        f"Total esperado del partido: {datos['tarjetas_esperadas_total']:.2f} tarjetas.",
        "",
        "Mercados de línea más probables (convención Grupo A: +N = N+1 o más, "
        "-N = N-1 o menos):",
        f"• TOTAL del partido: {_formatear_mercados(datos['mercados_total'])}.",
        f"• {n_local} (local): {_formatear_mercados(datos['mercados_local'])}.",
        f"• {n_visita} (visitante): {_formatear_mercados(datos['mercados_visitante'])}.",
        "",
        "Nota: el factor ÁRBITRO (el de mayor peso en tarjetas) y la INSTANCIA "
        "del torneo aún no se incluyen; se sumarán con datos reales.",
    ]

    return "\n".join(lineas_txt)

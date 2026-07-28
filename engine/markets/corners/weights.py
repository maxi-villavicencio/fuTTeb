"""Pesos y configuración del mercado: Córners.

TODO valor configurable vive aquí. El cálculo (calculator.py) NO debe contener
números mágicos: siempre lee de este módulo.
"""

# --- Ponderación "genera" vs "concede" ------------------------------------
# Los córners esperados de un equipo se estiman combinando:
#   - lo que ese equipo GENERA (según su localía), y
#   - lo que el rival CONCEDE (según la localía del rival).
# Ambos pesos deben sumar 1.0. Por defecto 50/50.
PESO_GENERA: float = 0.5
PESO_CONCEDE: float = 0.5

# --- Traducción a índice 0-100 --------------------------------------------
# Línea de referencia del mercado (total de córners del partido).
LINEA_CORNERS: float = 9.5

# Cuántos puntos de índice suma/resta cada córner de diferencia respecto de la
# línea. Ver la fórmula documentada en calculator.py.
SENSIBILIDAD_INDICE: float = 12.5

# Índice cuando los córners esperados caen JUSTO sobre la línea (neutral).
INDICE_BASE: float = 50.0

# Límites del índice.
INDICE_MIN: float = 0.0
INDICE_MAX: float = 100.0

# --- Fiabilidad -----------------------------------------------------------
# Mínimo de partidos históricos del tipo relevante para considerar el índice
# CONFIABLE: el local necesita al menos esta cantidad de partidos DE LOCAL, y
# el visitante al menos esta cantidad DE VISITANTE. Por debajo, el índice se
# calcula igual pero se marca como NO confiable, con una advertencia detallada.
MIN_PARTIDOS_CONFIABLE: int = 8


def validar_config() -> None:
    """Chequeo defensivo: los pesos deben sumar 1.0."""
    total = PESO_GENERA + PESO_CONCEDE
    if abs(total - 1.0) > 1e-9:
        raise ValueError(
            f"PESO_GENERA + PESO_CONCEDE debe sumar 1.0 (actual: {total})."
        )

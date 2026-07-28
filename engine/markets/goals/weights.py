"""Pesos y configuración del mercado: Goles.

TODO valor configurable vive aquí. El cálculo (calculator.py) NO debe contener
números mágicos: siempre lee de este módulo.
"""

# --- Ponderación ataque propio vs defensa del rival -----------------------
# Los goles esperados de un equipo se estiman combinando:
#   - lo que ese equipo MARCA (ataque propio, según su localía), y
#   - lo que el rival CONCEDE (defensa del rival, según la localía del rival).
# Ambos pesos deben sumar 1.0. Acordado: 60% ataque / 40% defensa.
PESO_ATAQUE: float = 0.6
PESO_DEFENSA: float = 0.4

# --- Matriz de Poisson ----------------------------------------------------
# Máximo de goles por equipo en la matriz de marcadores. El último casillero
# acumula la cola (P(>= max)), así la matriz suma ~1.0.
MAX_GOLES_MATRIZ: int = 8

# --- Mercado Over/Under ---------------------------------------------------
# Línea del total de goles del partido.
LINEA_OVER_UNDER: float = 2.5

# --- Rangos de goles totales ----------------------------------------------
# Los rangos NO se escriben a mano: se generan automáticamente como una familia
# de rangos contiguos del mismo ancho, inclusivos en ambos extremos, cubriendo
# desde 0 hasta el total máximo posible de la matriz Poisson.
#   ANCHO_RANGO = 2  -> 0-1, 2-3, 4-5, 6-7, ...
#   ANCHO_RANGO = 3  -> 0-2, 3-5, 6-8, ...
# Cambiar este valor recalcula los rangos solo.
ANCHO_RANGO: int = 2

# Cuántos marcadores y rangos mostrar en el "top" (ordenados por probabilidad).
TOP_MARCADORES: int = 5
TOP_RANGOS: int = 5

# --- Fiabilidad -----------------------------------------------------------
# Mismo criterio que córners: el local necesita al menos esta cantidad de
# partidos DE LOCAL y el visitante DE VISITANTE para un índice confiable.
MIN_PARTIDOS_CONFIABLE: int = 8


def validar_config() -> None:
    """Chequeo defensivo de la configuración."""
    total = PESO_ATAQUE + PESO_DEFENSA
    if abs(total - 1.0) > 1e-9:
        raise ValueError(
            f"PESO_ATAQUE + PESO_DEFENSA debe sumar 1.0 (actual: {total})."
        )
    if MAX_GOLES_MATRIZ < 1:
        raise ValueError("MAX_GOLES_MATRIZ debe ser >= 1.")
    if ANCHO_RANGO < 1:
        raise ValueError("ANCHO_RANGO debe ser >= 1.")

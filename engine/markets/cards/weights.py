"""Pesos y configuración del mercado: Tarjetas.

TODO valor configurable vive aquí. El cálculo (calculator.py) NO debe contener
números mágicos ni la convención de líneas (esa vive en engine.core.lineas).

La ponderación y el umbral de confiabilidad se REUTILIZAN de Goles para tener
una sola fuente de verdad (mismo método 60/40 y mismo criterio de fiabilidad).
"""

from engine.core import lineas
from engine.markets.goals import weights as goals_weights

# --- Ponderación "genera" (propias) vs "provoca" (las del rival) ----------
# 60% las tarjetas que el equipo recibe; 40% las que el rival suele provocar.
# Se reutilizan los pesos de Goles (60/40) como fuente única.
PESO_GENERA: float = goals_weights.PESO_ATAQUE     # 0.60
PESO_PROVOCA: float = goals_weights.PESO_DEFENSA   # 0.40

# --- Poisson --------------------------------------------------------------
# Máximo de tarjetas POR EQUIPO en la distribución de Poisson. El total del
# partido usa el doble (dos equipos). El último casillero acumula la cola.
MAX_TARJETAS_EQUIPO: int = 8

# --- Líneas ---------------------------------------------------------------
# Tarjetas usa la convención del GRUPO A (desplazada, con lado negativo).
# La lógica de la convención NO se copia: vive en engine.core.lineas.
GRUPO_LINEA: str = lineas.GRUPO_A

# Cuántos mercados de línea más probables devolver por cada distribución.
TOP_MERCADOS: int = 4

# Al elegir "los más probables" se descartan los mercados TRIVIALES (casi
# seguros o casi imposibles), que no aportan información: por ejemplo
# "15 o menos tarjetas" siempre se cumple (~100%). Se consideran informativos
# los mercados con probabilidad en el rango (INFERIOR, SUPERIOR). Configurable.
UMBRAL_TRIVIAL_SUPERIOR: float = 0.95
UMBRAL_TRIVIAL_INFERIOR: float = 0.05

# --- Fiabilidad -----------------------------------------------------------
# Mismo criterio que los demás mercados (reutilizado de Goles).
MIN_PARTIDOS_CONFIABLE: int = goals_weights.MIN_PARTIDOS_CONFIABLE


def validar_config() -> None:
    """Chequeo defensivo de la configuración."""
    total = PESO_GENERA + PESO_PROVOCA
    if abs(total - 1.0) > 1e-9:
        raise ValueError(
            f"PESO_GENERA + PESO_PROVOCA debe sumar 1.0 (actual: {total})."
        )
    if MAX_TARJETAS_EQUIPO < 1:
        raise ValueError("MAX_TARJETAS_EQUIPO debe ser >= 1.")

"""Pesos y configuración del mercado: Ambos equipos marcan (BTTS).

BTTS comparte el método con Goles (misma ponderación 60/40 y mismo umbral de
confiabilidad). Para tener UNA SOLA FUENTE DE VERDAD, estos valores NO se
redefinen aquí: se importan de la configuración de Goles. Si mañana se ajusta
la ponderación en Goles, BTTS la sigue automáticamente.
"""

from engine.markets.goals import weights as goals_weights

# Ponderación ataque propio / defensa del rival (reutilizada de Goles).
PESO_ATAQUE: float = goals_weights.PESO_ATAQUE
PESO_DEFENSA: float = goals_weights.PESO_DEFENSA

# Máximo de goles de la matriz Poisson (reutilizado de Goles) para que el
# número de BTTS coincida exactamente con el que calcula el mercado de Goles.
MAX_GOLES_MATRIZ: int = goals_weights.MAX_GOLES_MATRIZ

# Umbral de confiabilidad (mínimo de partidos del tipo relevante por equipo).
MIN_PARTIDOS_CONFIABLE: int = goals_weights.MIN_PARTIDOS_CONFIABLE

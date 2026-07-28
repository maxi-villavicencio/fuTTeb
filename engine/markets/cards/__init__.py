"""Mercado: Tarjetas.

Plugin de mercado independiente. Expone el cálculo del Índice de Apuesta
para el mercado de Tarjetas reutilizando la estructura común de todos los mercados:

    calculator.py   -> orquesta el cálculo y devuelve el resultado del engine
    weights.py      -> pesos/configuración de los factores del mercado
    rules.py        -> reglas y validaciones específicas del mercado
    simulator.py    -> simulación de probabilidades (p. ej. Montecarlo/Poisson)
    explanation.py  -> genera la explicación legible del índice

Este paquete NO debe importar nada de FastAPI ni del frontend.

Tarjetas reutiliza el motor Poisson compartido (engine.probability.poisson) y
la convención de líneas compartida (engine.core.lineas, Grupo A); no
reimplementa esa lógica.
"""

from .calculator import MARKET_CODE, calcular

__all__ = ["calcular", "MARKET_CODE"]

"""Bet Analyzer AI — Engine.

Módulo de inteligencia TOTALMENTE independiente del backend y del frontend.

El engine:
  * Lee datos históricos y de contexto (a través de ``engine.data``).
  * Calcula el "Índice de Apuesta" por mercado (plugins en ``engine.markets``).
  * Devuelve índice + probabilidades + explicación.

No predice resultados: evalúa la CALIDAD de una apuesta por mercado.

Regla de oro del proyecto: la web y la API NUNCA calculan; solo consumen lo
que devuelve el engine. Por eso este paquete no importa nada de FastAPI ni
del frontend y debe poder ejecutarse por sí solo.
"""

__all__ = ["core", "data", "markets", "backtesting"]

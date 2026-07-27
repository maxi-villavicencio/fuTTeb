"""Registro y descubrimiento de mercados.

Punto único donde el engine conoce qué mercados existen y cómo obtener su
calculadora. Permite añadir un mercado nuevo sin tocar el resto del sistema:
basta con registrarlo aquí (o descubrirlo automáticamente desde
``engine.markets``).
"""

# TODO: implementar el registro de mercados, por ejemplo:
#   - get_market(name) -> MarketCalculator
#   - available_markets() -> list[str]

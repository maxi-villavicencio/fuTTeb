"""Calculadora del mercado: Goles.

Punto de entrada del plugin. Debe implementar el protocolo definido en
engine.core.protocol (ver MarketCalculator). Recibe el contexto del
partido y los datos históricos (a través de un repositorio de engine.data)
y devuelve un MarketResult con: índice de apuesta, probabilidades y
explicación.

Regla de oro: aquí vive la inteligencia del mercado. La web y la API solo
consumen este resultado; nunca calculan.
"""

# TODO: implementar la clase Calculator que cumpla engine.core.protocol.MarketCalculator

"""Protocolo que todo mercado debe cumplir.

Define el CONTRATO común de los plugins de mercado. Cualquier mercado
(goles, córners, tarjetas, remates, BTTS, o uno nuevo) debe implementar esta
interfaz para poder ser descubierto y ejecutado de forma uniforme por el
engine.

La idea: el engine no conoce los detalles internos de cada mercado, solo
sabe que todos exponen la misma forma de "calcular".
"""

# TODO: definir el contrato del mercado, por ejemplo (esbozo):
#
#   from typing import Protocol
#   from engine.core.types import MatchContext, MarketResult
#
#   class MarketCalculator(Protocol):
#       """Contrato que cada mercado debe implementar."""
#
#       name: str  # identificador del mercado (p. ej. "goals")
#
#       def calculate(self, context: MatchContext) -> MarketResult:
#           """Devuelve el Índice de Apuesta + probabilidades + explicación."""
#           ...

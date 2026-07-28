"""Herramientas de probabilidad COMPARTIDAS del engine.

Piezas reutilizables por cualquier mercado (no específicas de uno solo). Hoy
contiene el motor de Poisson usado por el mercado de Goles; mañana lo podrán
reutilizar otros (p. ej. un plugin dedicado de BTTS).

Este paquete NO importa FastAPI ni nada del frontend.
"""

from . import poisson

__all__ = ["poisson"]

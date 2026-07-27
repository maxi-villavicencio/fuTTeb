"""Núcleo del engine (core).

Contiene los tipos, interfaces base y el "protocolo" que TODO mercado debe
cumplir. Es la pieza que garantiza que todos los plugins de mercado sean
intercambiables y consumibles de la misma forma.

    types.py     -> tipos de datos compartidos (contexto, resultado, etc.)
    protocol.py  -> el contrato (Protocol/ABC) que cada mercado implementa
    registry.py  -> registro/descubrimiento de mercados disponibles
"""

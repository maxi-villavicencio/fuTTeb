"""Mercados del engine (plugins).

Cada mercado es una carpeta independiente con la MISMA estructura interna
(calculator, weights, rules, simulator, explanation). Todos cumplen el
protocolo de ``engine.core.protocol`` para ser intercambiables.

Mercados incluidos:
    goals   -> Goles
    corners -> Córners
    cards   -> Tarjetas
    shots   -> Remates
    btts    -> Ambos equipos marcan (BTTS)

Para añadir un mercado nuevo, ver el paso a paso en el README de la raíz.
"""

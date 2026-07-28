"""Calculadora del mercado: Ambos equipos marcan (BTTS).

Este plugin NO reimplementa nada: es un empaquetado como mercado propio de un
cálculo que ya existe.

  - Los goles esperados (ponderación 60/40) se obtienen de la FUNCIÓN
    REUTILIZABLE de Goles: ``engine.markets.goals.calculator.goles_esperados_partido``.
  - La probabilidad de BTTS se obtiene del MOTOR POISSON COMPARTIDO
    ``engine.probability.poisson`` (misma matriz y misma función que usa Goles),
    de modo que el número coincide EXACTAMENTE con el que informa el mercado de
    Goles para los mismos equipos.

Lógica:
    1. goles esperados de local y visitante (reutilizados).
    2. matriz Poisson y P(ambos marcan) = P(local>=1) * P(visitante>=1).
    3. BTTS Sí = esa probabilidad; BTTS No = 1 - BTTS Sí.
    4. índice 0-100 = probabilidad de BTTS Sí en %.

Sin machine learning. No importa FastAPI ni el frontend.
"""

from sqlalchemy.engine import Engine

from engine.core.types import MarketResult
from engine.markets.goals.calculator import goles_esperados_partido
from engine.probability import poisson

from . import explanation, rules, weights

MARKET_CODE = "btts"


def calcular(
    home_team_id: int,
    away_team_id: int,
    engine: Engine | None = None,
) -> MarketResult:
    """Calcula el mercado BTTS para un enfrentamiento local vs visitante."""
    # --- 1: goles esperados (fuente única de verdad, ponderación 60/40) -----
    esperados = goles_esperados_partido(home_team_id, away_team_id, engine=engine)

    # --- 2: BTTS via el MISMO motor Poisson y la MISMA función que Goles ----
    # Reconstruir la matriz con el mismo máximo garantiza el mismo número que Goles.
    matriz = poisson.matriz_conjunta(
        esperados.lambda_local, esperados.lambda_visitante, weights.MAX_GOLES_MATRIZ
    )
    prob_si = poisson.prob_ambos_marcan(matriz)  # P(local>=1) * P(visitante>=1)
    prob_no = 1.0 - prob_si

    # Probabilidad de que cada equipo marque al menos 1 (para la explicación).
    # P(local=0) = suma de la fila 0; P(visitante=0) = suma de la columna 0.
    prob_local_marca = 1.0 - sum(matriz[0])
    prob_visitante_marca = 1.0 - sum(fila[0] for fila in matriz)

    # --- 3 y 4: índice = probabilidad de BTTS Sí en % -----------------------
    indice = prob_si * 100.0

    # --- Confiabilidad (mismo criterio que córners y goles) ----------------
    advertencias, confiable = rules.validar_confiabilidad(
        nombre_local=esperados.nombre_local,
        partidos_local=esperados.local_marca.partidos,
        nombre_visitante=esperados.nombre_visitante,
        partidos_visitante=esperados.visitante_marca.partidos,
    )

    valores = {
        "nombre_local": esperados.nombre_local,
        "nombre_visitante": esperados.nombre_visitante,
        # Componentes de las lambdas (para la explicación)
        "local_marca": esperados.local_marca.promedio,
        "local_marca_n": esperados.local_marca.partidos,
        "visitante_concede": esperados.visitante_concede.promedio,
        "visitante_concede_n": esperados.visitante_concede.partidos,
        "visitante_marca": esperados.visitante_marca.promedio,
        "visitante_marca_n": esperados.visitante_marca.partidos,
        "local_concede": esperados.local_concede.promedio,
        "local_concede_n": esperados.local_concede.partidos,
        # Goles esperados
        "goles_esperados_local": esperados.lambda_local,
        "goles_esperados_visitante": esperados.lambda_visitante,
        # Probabilidad de que cada equipo marque al menos 1
        "prob_local_marca": prob_local_marca,
        "prob_visitante_marca": prob_visitante_marca,
        # Mercado BTTS
        "prob_si": prob_si,
        "prob_no": prob_no,
        "indice": indice,
    }

    texto = explanation.generar_explicacion(valores)

    return MarketResult(
        market=MARKET_CODE,
        indice=indice,
        valores=valores,
        explicacion=texto,
        advertencias=advertencias,
        confiable=confiable,
    )

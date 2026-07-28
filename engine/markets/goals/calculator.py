"""Calculadora del mercado: Goles.

Estima los goles esperados de cada equipo mediante un PROMEDIO PONDERADO
EXPLICABLE (60% ataque propio / 40% defensa del rival) y, sobre esos valores
(lambdas), aplica el motor de POISSON compartido para obtener la matriz de
marcadores. De la matriz deriva 4 mercados:

    - Over/Under (por defecto 2.5)  -> probabilidad + índice 0-100
    - BTTS (ambos marcan)           -> probabilidad + índice 0-100
    - Marcador exacto más probable  -> (i, j) y su probabilidad
    - Rango de goles más probable   -> etiqueta y su probabilidad

Sin machine learning. Lee datos vía engine.data (nunca SQL suelto aquí) y
devuelve un MarketResult estándar. El índice "titular" del MarketResult es el
de Over/Under; el resto de los mercados viaja en ``valores``.
"""

from sqlalchemy.engine import Engine

from engine.core.types import MarketResult
from engine.data import statistics_repository as repo
from engine.data.statistics_repository import PromedioMuestra
from engine.probability import poisson

from . import explanation, rules, weights

MARKET_CODE = "goals"


def _combinar(marca: PromedioMuestra, concede: PromedioMuestra) -> float:
    """Promedio ponderado 60/40 entre ataque propio (marca) y defensa rival (concede).

    Si a un componente le faltan datos, se renormalizan los pesos sobre los
    disponibles (no se hunde el valor a 0). Si faltan ambos, devuelve 0.0.
    """
    componentes = []
    if marca.hay_datos:
        componentes.append((weights.PESO_ATAQUE, marca.promedio))
    if concede.hay_datos:
        componentes.append((weights.PESO_DEFENSA, concede.promedio))

    if not componentes:
        return 0.0

    peso_total = sum(peso for peso, _ in componentes)
    return sum(peso * valor for peso, valor in componentes) / peso_total


def _generar_rangos(total_maximo: int, ancho: int) -> list[tuple[str, int, int]]:
    """Genera una familia de rangos contiguos del mismo ancho, sin solapamiento.

    Los rangos son inclusivos en ambos extremos y cubren de 0 a ``total_maximo``.
    NO están hardcodeados: se derivan del ancho configurado.
        ancho=2 -> (0-1), (2-3), (4-5), ...
        ancho=3 -> (0-2), (3-5), (6-8), ...

    Returns:
        Lista de (etiqueta, minimo, maximo).
    """
    rangos: list[tuple[str, int, int]] = []
    inicio = 0
    while inicio <= total_maximo:
        fin = inicio + ancho - 1
        rangos.append((f"{inicio}-{fin}", inicio, fin))
        inicio += ancho
    return rangos


def _probabilidades_por_rango(
    matriz: list[list[float]], rangos: list[tuple[str, int, int]]
) -> list[tuple[str, float]]:
    """Probabilidad de cada rango sumando los marcadores cuyo total cae dentro.

    Como los rangos son contiguos y no se solapan, las probabilidades de TODOS
    los rangos suman ~1.0 (100%). El que muestra el mercado es solo el top-N, que
    lógicamente suma menos.
    """
    resultados: list[tuple[str, float]] = []
    for etiqueta, minimo, maximo in rangos:
        prob = 0.0
        for i, fila in enumerate(matriz):
            for j, p in enumerate(fila):
                if minimo <= (i + j) <= maximo:
                    prob += p
        resultados.append((etiqueta, prob))
    return resultados


def _top_marcadores(
    matriz: list[list[float]], n: int
) -> list[tuple[int, int, float]]:
    """Devuelve los ``n`` marcadores más probables como (local, visitante, prob)."""
    todos = [
        (i, j, p)
        for i, fila in enumerate(matriz)
        for j, p in enumerate(fila)
    ]
    todos.sort(key=lambda t: t[2], reverse=True)
    return todos[:n]


def calcular(
    home_team_id: int,
    away_team_id: int,
    engine: Engine | None = None,
) -> MarketResult:
    """Calcula el mercado de Goles para un enfrentamiento local vs visitante."""
    weights.validar_config()

    # --- 1 y 2: goles esperados (lambdas) via promedio ponderado 60/40 -----
    local_marca = repo.goles_marcados(home_team_id, de_local=True, engine=engine)
    visitante_concede = repo.goles_concedidos(away_team_id, de_local=False, engine=engine)
    visitante_marca = repo.goles_marcados(away_team_id, de_local=False, engine=engine)
    local_concede = repo.goles_concedidos(home_team_id, de_local=True, engine=engine)

    lambda_local = _combinar(local_marca, visitante_concede)
    lambda_visitante = _combinar(visitante_marca, local_concede)

    # --- 3: matriz de marcadores via Poisson (motor compartido) ------------
    matriz = poisson.matriz_conjunta(
        lambda_local, lambda_visitante, weights.MAX_GOLES_MATRIZ
    )

    # --- 4: derivar los 4 mercados de la matriz ----------------------------
    # Over/Under
    prob_over = poisson.prob_total_mayor(matriz, weights.LINEA_OVER_UNDER)
    indice_over = prob_over * 100.0  # índice = probabilidad en %

    # BTTS
    prob_btts = poisson.prob_ambos_marcan(matriz)
    indice_btts = prob_btts * 100.0

    # Marcador exacto: los TOP_MARCADORES más probables (mayor a menor)
    top_marcadores = _top_marcadores(matriz, weights.TOP_MARCADORES)

    # Rangos de goles: familia contigua generada por ancho configurable.
    # total_maximo = suma máxima posible de la matriz (ambos equipos al máximo).
    total_maximo = 2 * weights.MAX_GOLES_MATRIZ
    rangos_todos = _probabilidades_por_rango(
        matriz, _generar_rangos(total_maximo, weights.ANCHO_RANGO)
    )
    # Solo el top-N, ordenado de mayor a menor probabilidad.
    rangos_top = sorted(rangos_todos, key=lambda par: par[1], reverse=True)[
        : weights.TOP_RANGOS
    ]

    # --- Confiabilidad (mismo criterio que córners) ------------------------
    nombre_local = repo.nombre_equipo(home_team_id, engine=engine)
    nombre_visitante = repo.nombre_equipo(away_team_id, engine=engine)
    advertencias, confiable = rules.validar_confiabilidad(
        nombre_local=nombre_local,
        partidos_local=local_marca.partidos,
        nombre_visitante=nombre_visitante,
        partidos_visitante=visitante_marca.partidos,
    )

    # --- Empaquetado de valores (transparencia total) ----------------------
    valores = {
        "nombre_local": nombre_local,
        "nombre_visitante": nombre_visitante,
        # Componentes de las lambdas
        "local_marca": local_marca.promedio,
        "local_marca_n": local_marca.partidos,
        "visitante_concede": visitante_concede.promedio,
        "visitante_concede_n": visitante_concede.partidos,
        "visitante_marca": visitante_marca.promedio,
        "visitante_marca_n": visitante_marca.partidos,
        "local_concede": local_concede.promedio,
        "local_concede_n": local_concede.partidos,
        # Goles esperados
        "goles_esperados_local": lambda_local,
        "goles_esperados_visitante": lambda_visitante,
        "goles_esperados_total": lambda_local + lambda_visitante,
        # Mercado 1: Over/Under
        "over_under": {
            "linea": weights.LINEA_OVER_UNDER,
            "prob_over": prob_over,
            "prob_under": 1.0 - prob_over,
            "indice": indice_over,
        },
        # Mercado 2: BTTS
        "btts": {
            "prob_si": prob_btts,
            "prob_no": 1.0 - prob_btts,
            "indice": indice_btts,
        },
        # Mercado 3: los TOP_MARCADORES exactos más probables (mayor a menor)
        "marcadores_top": [
            {"local": i, "visitante": j, "texto": f"{i}-{j}", "prob": p}
            for i, j, p in top_marcadores
        ],
        # Mercado 4: rangos de goles. Ancho configurable (weights.ANCHO_RANGO);
        # se muestran solo los TOP_RANGOS más probables. La familia completa de
        # rangos suma ~1.0; este top-N suma menos (es un subconjunto).
        "ancho_rango": weights.ANCHO_RANGO,
        "rangos_top": [{"rango": etq, "prob": p} for etq, p in rangos_top],
        # Verificación
        "suma_probabilidades": poisson.suma_matriz(matriz),
    }

    texto = explanation.generar_explicacion(valores)

    # El índice titular del mercado Goles es el de Over/Under.
    return MarketResult(
        market=MARKET_CODE,
        indice=indice_over,
        valores=valores,
        explicacion=texto,
        advertencias=advertencias,
        confiable=confiable,
    )

"""Calculadora del mercado: Tarjetas.

Estima las tarjetas esperadas (amarilla o roja = 1) de cada equipo mediante un
PROMEDIO PONDERADO EXPLICABLE (60% propias / 40% las que provoca el rival) y,
sobre esas medias (lambdas), aplica el motor de POISSON compartido para obtener
la distribución de tarjetas de: el TOTAL del partido, el TOTAL del LOCAL y el
TOTAL del VISITANTE.

Para cada distribución usa el MÓDULO DE LÍNEAS compartido (Grupo A) y devuelve
los mercados de línea (+N/-N) más probables. Ni la convención de líneas ni el
Poisson se reimplementan acá.

Sin machine learning. No importa FastAPI ni el frontend.

PENDIENTES (a incorporar con datos reales; NO implementar todavía):
  TODO: factor ÁRBITRO. Es el factor de MAYOR peso en tarjetas (cada árbitro
        tiene su propia tendencia). Se sumará cuando haya datos reales de
        árbitros por partido.
  TODO: factor INSTANCIA DEL TORNEO (copa/liga, partidos decisivos). Mayor
        tensión = más tarjetas. Se sumará con datos que incluyan copas.
"""

from sqlalchemy.engine import Engine

from engine.core import lineas
from engine.core.types import MarketResult
from engine.data import statistics_repository as repo
from engine.data.statistics_repository import PromedioMuestra
from engine.probability import poisson

from . import explanation, rules, weights

MARKET_CODE = "cards"


def _combinar(genera: PromedioMuestra, provoca: PromedioMuestra) -> float:
    """Promedio ponderado 60/40 entre tarjetas propias y las que provoca el rival.

    Si a un componente le faltan datos, renormaliza los pesos sobre los
    disponibles. Si faltan ambos, devuelve 0.0.
    """
    componentes = []
    if genera.hay_datos:
        componentes.append((weights.PESO_GENERA, genera.promedio))
    if provoca.hay_datos:
        componentes.append((weights.PESO_PROVOCA, provoca.promedio))

    if not componentes:
        return 0.0

    peso_total = sum(peso for peso, _ in componentes)
    return sum(peso * valor for peso, valor in componentes) / peso_total


def _top_lineas(dist: list[float], max_conteo: int, n: int) -> list[dict]:
    """Calcula la probabilidad de cada línea (Grupo A) y devuelve las n más probables.

    Usa SIEMPRE el módulo compartido engine.core.lineas (no copia la convención).

    Se descartan los mercados TRIVIALES (prob >= SUPERIOR o <= INFERIOR): son
    casi seguros o casi imposibles y no aportan información (p. ej. "15 o menos
    tarjetas" siempre se cumple). Entre los INFORMATIVOS se devuelven los n más
    probables. Si no quedara ninguno informativo, se cae de nuevo al top-n bruto.
    """
    etiquetas = lineas.generar_etiquetas(weights.GRUPO_LINEA, max_conteo)
    evaluadas = [
        {
            "linea": etq,
            "descripcion": lineas.descripcion_linea(weights.GRUPO_LINEA, etq),
            "prob": lineas.probabilidad_linea(weights.GRUPO_LINEA, etq, dist),
        }
        for etq in etiquetas
    ]
    informativas = [
        m
        for m in evaluadas
        if weights.UMBRAL_TRIVIAL_INFERIOR <= m["prob"] <= weights.UMBRAL_TRIVIAL_SUPERIOR
    ]
    base = informativas if informativas else evaluadas
    base.sort(key=lambda m: m["prob"], reverse=True)
    return base[:n]


def calcular(
    home_team_id: int,
    away_team_id: int,
    engine: Engine | None = None,
) -> MarketResult:
    """Calcula el mercado de Tarjetas para un enfrentamiento local vs visitante."""
    weights.validar_config()

    # --- 1 y 2: tarjetas esperadas (lambdas) via promedio ponderado 60/40 ---
    local_genera = repo.tarjetas_generadas(home_team_id, de_local=True, engine=engine)
    visitante_provoca = repo.tarjetas_provocadas(away_team_id, de_local=False, engine=engine)
    visitante_genera = repo.tarjetas_generadas(away_team_id, de_local=False, engine=engine)
    local_provoca = repo.tarjetas_provocadas(home_team_id, de_local=True, engine=engine)

    lambda_local = _combinar(local_genera, visitante_provoca)
    lambda_visitante = _combinar(visitante_genera, local_provoca)
    lambda_total = lambda_local + lambda_visitante

    # --- 3 y 4: distribuciones Poisson (total, local, visitante) ------------
    max_equipo = weights.MAX_TARJETAS_EQUIPO
    max_total = 2 * max_equipo  # el total del partido llega al doble
    dist_local = poisson.distribucion(lambda_local, max_equipo)
    dist_visitante = poisson.distribucion(lambda_visitante, max_equipo)
    dist_total = poisson.distribucion(lambda_total, max_total)

    # --- 5: mercados de línea (Grupo A) más probables por distribución ------
    top_total = _top_lineas(dist_total, max_total, weights.TOP_MERCADOS)
    top_local = _top_lineas(dist_local, max_equipo, weights.TOP_MERCADOS)
    top_visitante = _top_lineas(dist_visitante, max_equipo, weights.TOP_MERCADOS)

    # --- Confiabilidad (mismo criterio que córners y goles) ----------------
    nombre_local = repo.nombre_equipo(home_team_id, engine=engine)
    nombre_visitante = repo.nombre_equipo(away_team_id, engine=engine)
    advertencias, confiable = rules.validar_confiabilidad(
        nombre_local=nombre_local,
        partidos_local=local_genera.partidos,
        nombre_visitante=nombre_visitante,
        partidos_visitante=visitante_genera.partidos,
    )

    # Índice titular del mercado Tarjetas: probabilidad (en %) del mercado de
    # línea más probable del TOTAL del partido (la "apuesta más segura").
    indice = (top_total[0]["prob"] * 100.0) if top_total else 0.0

    valores = {
        "nombre_local": nombre_local,
        "nombre_visitante": nombre_visitante,
        # Componentes de las lambdas (para la explicación)
        "local_genera": local_genera.promedio,
        "local_genera_n": local_genera.partidos,
        "visitante_provoca": visitante_provoca.promedio,
        "visitante_provoca_n": visitante_provoca.partidos,
        "visitante_genera": visitante_genera.promedio,
        "visitante_genera_n": visitante_genera.partidos,
        "local_provoca": local_provoca.promedio,
        "local_provoca_n": local_provoca.partidos,
        # Tarjetas esperadas
        "tarjetas_esperadas_local": lambda_local,
        "tarjetas_esperadas_visitante": lambda_visitante,
        "tarjetas_esperadas_total": lambda_total,
        # Mercados de línea más probables por distribución
        "mercados_total": top_total,
        "mercados_local": top_local,
        "mercados_visitante": top_visitante,
        # Verificación de que cada distribución suma ~1.0
        "suma_dist_total": sum(dist_total),
        "suma_dist_local": sum(dist_local),
        "suma_dist_visitante": sum(dist_visitante),
        # Config usada (útil para el test)
        "max_equipo": max_equipo,
        "max_total": max_total,
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

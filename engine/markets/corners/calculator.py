"""Calculadora del mercado: Córners.

Corazón del plugin. Estima los córners esperados de un partido mediante un
PROMEDIO PONDERADO EXPLICABLE (sin machine learning) y los traduce a un índice
0-100. Lee los datos a través de ``engine.data.statistics_repository`` (nunca
SQL suelto aquí) y devuelve un ``MarketResult`` estándar.

Método (fijo, acordado):
  1. Local: promedio de córners que GENERA de local (is_home=1).
  2. Visitante: promedio de córners que CONCEDE de visitante (córners del rival
     en sus partidos de visitante, is_home=0).
  3. Esperados del local = ponderado(genera_local, concede_visitante).
  4. Simétrico para el visitante.
  5. Totales = esperados_local + esperados_visitante.
  6. Índice 0-100 según cuánto superan los totales a la línea (ver fórmula).

Regla de oro: aquí vive la inteligencia del mercado. La web/API solo consumen.
"""

from sqlalchemy.engine import Engine

from engine.core.types import MarketResult
from engine.data import statistics_repository as repo
from engine.data.statistics_repository import PromedioMuestra

from . import explanation, rules, weights

MARKET_CODE = "corners"


def _combinar(genera: PromedioMuestra, concede: PromedioMuestra) -> float:
    """Promedio ponderado entre lo que un equipo genera y lo que el rival concede.

    Usa los pesos de ``weights``. Si a un componente le faltan datos, se
    renormalizan los pesos sobre los componentes disponibles (así el resultado
    no se hunde a 0 por un solo dato ausente). Si faltan ambos, devuelve 0.0.
    """
    componentes = []
    if genera.hay_datos:
        componentes.append((weights.PESO_GENERA, genera.promedio))
    if concede.hay_datos:
        componentes.append((weights.PESO_CONCEDE, concede.promedio))

    if not componentes:
        return 0.0

    peso_total = sum(peso for peso, _ in componentes)
    return sum(peso * valor for peso, valor in componentes) / peso_total


def _a_indice(corners_totales: float) -> float:
    """Traduce los córners totales esperados a un índice 0-100.

    Fórmula (transparente y documentada):

        indice = INDICE_BASE + SENSIBILIDAD_INDICE * (totales - LINEA_CORNERS)

    - En la línea (totales == LINEA_CORNERS) el índice es INDICE_BASE (50).
    - Cada córner por ENCIMA de la línea suma SENSIBILIDAD_INDICE puntos.
    - Cada córner por DEBAJO los resta.
    - Se recorta al rango [INDICE_MIN, INDICE_MAX] (0-100).
    """
    bruto = weights.INDICE_BASE + weights.SENSIBILIDAD_INDICE * (
        corners_totales - weights.LINEA_CORNERS
    )
    return max(weights.INDICE_MIN, min(weights.INDICE_MAX, bruto))


def calcular(
    home_team_id: int,
    away_team_id: int,
    engine: Engine | None = None,
) -> MarketResult:
    """Calcula el índice de córners para un enfrentamiento local vs visitante.

    Args:
        home_team_id: id del equipo local.
        away_team_id: id del equipo visitante.
        engine:       Engine de SQLAlchemy opcional (para tests). Si es None,
                      usa la conexión compartida del engine.

    Returns:
        MarketResult con valores intermedios, índice, explicación y advertencias.
    """
    weights.validar_config()

    # --- 1 y 2: lecturas crudas desde el repositorio -----------------------
    local_genera = repo.corners_generados(home_team_id, de_local=True, engine=engine)
    visitante_concede = repo.corners_concedidos(away_team_id, de_local=False, engine=engine)
    visitante_genera = repo.corners_generados(away_team_id, de_local=False, engine=engine)
    local_concede = repo.corners_concedidos(home_team_id, de_local=True, engine=engine)

    # --- 3 y 4: esperados por equipo (promedio ponderado) ------------------
    esperados_local = _combinar(local_genera, visitante_concede)
    esperados_visitante = _combinar(visitante_genera, local_concede)

    # --- 5: totales --------------------------------------------------------
    corners_totales = esperados_local + esperados_visitante

    # --- 6: índice ---------------------------------------------------------
    indice = _a_indice(corners_totales)

    # --- Validación de fiabilidad -----------------------------------------
    # El local se juzga por sus partidos DE LOCAL (base de "genera de local");
    # el visitante, por sus partidos DE VISITANTE (base de "genera de visitante").
    nombre_local = repo.nombre_equipo(home_team_id, engine=engine)
    nombre_visitante = repo.nombre_equipo(away_team_id, engine=engine)
    advertencias, confiable = rules.validar_confiabilidad(
        nombre_local=nombre_local,
        partidos_local=local_genera.partidos,
        nombre_visitante=nombre_visitante,
        partidos_visitante=visitante_genera.partidos,
    )

    # --- Empaquetado de valores (transparencia total) ----------------------
    valores = {
        "nombre_local": nombre_local,
        "nombre_visitante": nombre_visitante,
        "local_genera": local_genera.promedio,
        "local_genera_n": local_genera.partidos,
        "visitante_concede": visitante_concede.promedio,
        "visitante_concede_n": visitante_concede.partidos,
        "visitante_genera": visitante_genera.promedio,
        "visitante_genera_n": visitante_genera.partidos,
        "local_concede": local_concede.promedio,
        "local_concede_n": local_concede.partidos,
        "esperados_local": esperados_local,
        "esperados_visitante": esperados_visitante,
        "corners_totales": corners_totales,
        "linea": weights.LINEA_CORNERS,
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

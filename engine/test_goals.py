"""Prueba del plugin de Goles sobre los datos de prueba del seed.

Ejecutar desde la raíz del proyecto:

    python engine/test_goals.py

Muestra, para un par de enfrentamientos:
  - goles esperados de cada equipo,
  - los 4 mercados (Over/Under, BTTS, marcador exacto, rango) con
    índices/probabilidades,
  - la explicación en español,
  - y una VERIFICACIÓN de que la matriz de marcadores suma ~1.0 (100%).
Si no suma ~1.0, avisa que hay un error en el Poisson.
"""

import sys
from pathlib import Path

# Permitir ejecutar como script desde la raíz del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.data import statistics_repository as repo  # noqa: E402
from engine.markets.goals import calcular  # noqa: E402
from engine.markets.goals import weights as goals_weights  # noqa: E402
from engine.probability import poisson  # noqa: E402

ENFRENTAMIENTOS = [
    ("River", "Boca"),
    ("San Lorenzo", "Independiente"),
    ("Racing", "Vélez"),
]

TOLERANCIA = 0.01  # ±1% para considerar que la matriz suma ~100%


def _verificar_matriz(resultado) -> bool:
    """Reconstruye la matriz desde las lambdas y verifica que sume ~1.0."""
    ll = resultado.valores["goles_esperados_local"]
    lv = resultado.valores["goles_esperados_visitante"]
    matriz = poisson.matriz_conjunta(ll, lv, goals_weights.MAX_GOLES_MATRIZ)
    suma = poisson.suma_matriz(matriz)
    ok = abs(suma - 1.0) <= TOLERANCIA
    if ok:
        print(f"✅ Verificación Poisson: la matriz suma {suma:.4f} (~100%). Correcto.")
    else:
        print(f"❌ Verificación Poisson: la matriz suma {suma:.4f}, "
              f"debería ser ~1.0. ¡Hay un error en el Poisson!")
    return ok


def _analizar(local_nombre: str, visitante_nombre: str) -> bool:
    local_id = repo.id_por_nombre_corto(local_nombre)
    visitante_id = repo.id_por_nombre_corto(visitante_nombre)

    print("=" * 66)
    print(f" {local_nombre} (local)  vs  {visitante_nombre} (visitante)")
    print("=" * 66)

    if local_id is None or visitante_id is None:
        faltan = local_nombre if local_id is None else visitante_nombre
        print(f"⚠️  No se encontró el equipo «{faltan}». ¿Corriste el seed?\n")
        return False

    r = calcular(local_id, visitante_id)
    v = r.valores
    ou, btts = v["over_under"], v["btts"]

    print(f"Goles esperados local     : {v['goles_esperados_local']:.2f}")
    print(f"Goles esperados visitante : {v['goles_esperados_visitante']:.2f}")
    print(f"Goles esperados TOTAL     : {v['goles_esperados_total']:.2f}")
    print(f"Confiable                 : {'sí' if r.confiable else 'NO'}")
    print("-" * 66)
    print("Mercados:")
    print(f"  Over/Under {ou['linea']}   : Over {ou['prob_over']:.0%} / "
          f"Under {ou['prob_under']:.0%}  → índice {ou['indice']:.0f}/100")
    print(f"  BTTS (ambos)     : Sí {btts['prob_si']:.0%} / "
          f"No {btts['prob_no']:.0%}  → índice {btts['indice']:.0f}/100")
    print("  5 marcadores más probables:")
    for m in v["marcadores_top"]:
        print(f"      {m['texto']} : {m['prob']:.1%}")
    print(f"  5 rangos más probables (ancho {v['ancho_rango']}):")
    for x in v["rangos_top"]:
        print(f"      {x['rango']} goles : {x['prob']:.1%}")
    print("-" * 66)
    print(_verificar_matriz(r))  # imprime True/False además del mensaje interno
    print("\n--- Explicación ---")
    print(r.explicacion)
    if r.advertencias:
        print("\n--- Advertencias ---")
        for adv in r.advertencias:
            print(f"  • {adv}")
    print()

    return abs(v["suma_probabilidades"] - 1.0) <= TOLERANCIA


def main() -> int:
    try:
        todo_ok = True
        for local, visitante in ENFRENTAMIENTOS:
            if not _analizar(local, visitante):
                todo_ok = False
        return 0 if todo_ok else 1
    except Exception as exc:
        print(f"❌ ERROR ejecutando la prueba: {exc}")
        print("Revisá que la base tenga los datos de prueba (database/05_seed_test_data.sql).")
        return 1


if __name__ == "__main__":
    sys.exit(main())

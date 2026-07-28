"""Prueba del plugin de BTTS sobre los datos de prueba del seed.

Ejecutar desde la raíz del proyecto:

    python engine/test_btts.py

Muestra, para un par de enfrentamientos: goles esperados, prob BTTS Sí/No,
índice y explicación.

VERIFICACIÓN DE COHERENCIA: el BTTS de este plugin debe COINCIDIR (mismo número)
con el que ya calcula el plugin de Goles para los mismos equipos. Imprime ambos
y confirma que son iguales. Si difieren, hay duplicación mal hecha.
"""

import sys
from pathlib import Path

# Permitir ejecutar como script desde la raíz del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.data import statistics_repository as repo  # noqa: E402
from engine.markets.btts import calcular as calcular_btts  # noqa: E402
from engine.markets.goals import calcular as calcular_goals  # noqa: E402

ENFRENTAMIENTOS = [
    ("River", "Boca"),
    ("San Lorenzo", "Independiente"),
    ("Racing", "Vélez"),
]

TOLERANCIA = 1e-9  # deben ser el MISMO número (no solo parecido)


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

    r = calcular_btts(local_id, visitante_id)
    v = r.valores

    print(f"Goles esperados local     : {v['goles_esperados_local']:.2f}")
    print(f"Goles esperados visitante : {v['goles_esperados_visitante']:.2f}")
    print(f"BTTS Sí                   : {v['prob_si']:.1%}")
    print(f"BTTS No                   : {v['prob_no']:.1%}")
    print(f"ÍNDICE                    : {r.indice:.0f}/100")
    print(f"Confiable                 : {'sí' if r.confiable else 'NO'}")

    # --- Verificación de coherencia con el plugin de Goles ----------------
    rg = calcular_goals(local_id, visitante_id)
    btts_desde_goals = rg.valores["btts"]["prob_si"]
    btts_desde_btts = v["prob_si"]
    coincide = abs(btts_desde_goals - btts_desde_btts) <= TOLERANCIA

    print("-" * 66)
    print("Coherencia BTTS (plugin BTTS vs plugin Goles):")
    print(f"  plugin BTTS  : {btts_desde_btts:.10f}")
    print(f"  plugin Goles : {btts_desde_goals:.10f}")
    if coincide:
        print("  ✅ COINCIDEN: mismo número, sin duplicación.")
    else:
        print("  ❌ DIFIEREN: hay duplicación mal hecha en el cálculo de BTTS.")

    print("\n--- Explicación ---")
    print(r.explicacion)
    if r.advertencias:
        print("\n--- Advertencias ---")
        for adv in r.advertencias:
            print(f"  • {adv}")
    print()

    return coincide


def main() -> int:
    try:
        todo_ok = True
        for local, visitante in ENFRENTAMIENTOS:
            if not _analizar(local, visitante):
                todo_ok = False
        print("=" * 66)
        if todo_ok:
            print("✅ Todos los BTTS coinciden con el plugin de Goles.")
        else:
            print("❌ Hay diferencias: revisar la reutilización del cálculo.")
        return 0 if todo_ok else 1
    except Exception as exc:
        print(f"❌ ERROR ejecutando la prueba: {exc}")
        print("Revisá que la base tenga los datos de prueba (database/05_seed_test_data.sql).")
        return 1


if __name__ == "__main__":
    sys.exit(main())

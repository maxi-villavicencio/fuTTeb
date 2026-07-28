"""Prueba del plugin de Tarjetas sobre los datos de prueba del seed.

Ejecutar desde la raíz del proyecto:

    python engine/test_cards.py

Muestra, para un par de enfrentamientos: tarjetas esperadas (local, visitante,
total), confiabilidad, y para TOTAL/LOCAL/VISITANTE los 4 mercados de línea más
probables con %. Verifica que cada distribución de Poisson suma ~100%.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.data import statistics_repository as repo  # noqa: E402
from engine.markets.cards import calcular  # noqa: E402

ENFRENTAMIENTOS = [
    ("River", "Boca"),
    ("San Lorenzo", "Independiente"),
    ("Racing", "Vélez"),
]

TOLERANCIA = 0.01


def _imprimir_mercados(titulo: str, mercados: list[dict]) -> None:
    print(f"  {titulo}:")
    for m in mercados:
        print(f"      {m['linea']:>4}  ({m['descripcion']:<11}) : {m['prob']:.1%}")


def _analizar(local_nombre: str, visitante_nombre: str) -> bool:
    local_id = repo.id_por_nombre_corto(local_nombre)
    visitante_id = repo.id_por_nombre_corto(visitante_nombre)

    print("=" * 68)
    print(f" {local_nombre} (local)  vs  {visitante_nombre} (visitante)")
    print("=" * 68)

    if local_id is None or visitante_id is None:
        faltan = local_nombre if local_id is None else visitante_nombre
        print(f"⚠️  No se encontró el equipo «{faltan}». ¿Corriste el seed?\n")
        return False

    r = calcular(local_id, visitante_id)
    v = r.valores

    print(f"Tarjetas esperadas local     : {v['tarjetas_esperadas_local']:.2f}")
    print(f"Tarjetas esperadas visitante : {v['tarjetas_esperadas_visitante']:.2f}")
    print(f"Tarjetas esperadas TOTAL     : {v['tarjetas_esperadas_total']:.2f}")
    print(f"Confiable                    : {'sí' if r.confiable else 'NO'}")
    print("-" * 68)
    print("Mercados de línea más probables (Grupo A: +N = N+1 o más, -N = N-1 o menos):")
    _imprimir_mercados("TOTAL del partido", v["mercados_total"])
    _imprimir_mercados(f"{local_nombre} (local)", v["mercados_local"])
    _imprimir_mercados(f"{visitante_nombre} (visitante)", v["mercados_visitante"])
    print("-" * 68)

    # Verificación: cada distribución de Poisson debe sumar ~1.0.
    sumas = {
        "total": v["suma_dist_total"],
        "local": v["suma_dist_local"],
        "visitante": v["suma_dist_visitante"],
    }
    todo_ok = True
    for nombre, suma in sumas.items():
        ok = abs(suma - 1.0) <= TOLERANCIA
        todo_ok = todo_ok and ok
        marca = "✅" if ok else "❌"
        print(f"  {marca} Distribución {nombre}: suma {suma:.4f} (~100%).")
    if not todo_ok:
        print("  ❌ Alguna distribución no suma ~1.0: revisar el Poisson.")

    print("\n--- Explicación ---")
    print(r.explicacion)
    if r.advertencias:
        print("\n--- Advertencias ---")
        for adv in r.advertencias:
            print(f"  • {adv}")
    print()

    return todo_ok


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

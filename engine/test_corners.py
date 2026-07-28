"""Prueba del plugin de Córners sobre los datos de prueba del seed.

Ejecutar desde la raíz del proyecto:

    python engine/test_corners.py

Corre el cálculo para un par de enfrentamientos y muestra por consola los
córners esperados, el índice 0-100 y la explicación en español.
"""

import sys
from pathlib import Path

# Permitir ejecutar como script desde la raíz del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.data import statistics_repository as repo  # noqa: E402
from engine.markets.corners import calcular  # noqa: E402

# Enfrentamientos de prueba (local, visitante) por nombre corto del seed.
ENFRENTAMIENTOS = [
    ("River", "Boca"),
    ("San Lorenzo", "Independiente"),
    ("Racing", "Vélez"),
]


def _analizar(local_nombre: str, visitante_nombre: str) -> None:
    local_id = repo.id_por_nombre_corto(local_nombre)
    visitante_id = repo.id_por_nombre_corto(visitante_nombre)

    print("=" * 64)
    print(f" {local_nombre} (local)  vs  {visitante_nombre} (visitante)")
    print("=" * 64)

    if local_id is None or visitante_id is None:
        faltan = local_nombre if local_id is None else visitante_nombre
        print(f"⚠️  No se encontró el equipo «{faltan}» en la base. ¿Corriste el seed?\n")
        return

    resultado = calcular(local_id, visitante_id)

    print(f"Córners esperados local     : {resultado.valores['esperados_local']:.2f}")
    print(f"Córners esperados visitante : {resultado.valores['esperados_visitante']:.2f}")
    print(f"Córners TOTALES esperados   : {resultado.valores['corners_totales']:.2f}")
    print(f"ÍNDICE                      : {resultado.indice:.0f}/100")
    print(f"Confiable                   : {'sí' if resultado.confiable else 'NO'}")
    print("\n--- Explicación ---")
    print(resultado.explicacion)
    if resultado.advertencias:
        print("\n--- Advertencias ---")
        for adv in resultado.advertencias:
            print(f"  • {adv}")
    print()


def main() -> int:
    try:
        for local, visitante in ENFRENTAMIENTOS:
            _analizar(local, visitante)
        return 0
    except Exception as exc:  # red de seguridad para la prueba
        print(f"❌ ERROR ejecutando la prueba: {exc}")
        print("Revisá que la base tenga los datos de prueba (database/05_seed_test_data.sql).")
        return 1


if __name__ == "__main__":
    sys.exit(main())

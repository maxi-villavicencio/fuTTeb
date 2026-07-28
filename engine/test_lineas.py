"""Prueba del módulo compartido de convención de líneas (engine/core/lineas.py).

Ejecutar desde la raíz del proyecto:

    python engine/test_lineas.py

Verifica casos conocidos de ambos grupos.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.core import lineas  # noqa: E402

EPS = 1e-9
_fallos = 0


def _check(descripcion: str, obtenido, esperado) -> None:
    global _fallos
    if isinstance(esperado, float):
        ok = abs(obtenido - esperado) <= EPS
    else:
        ok = obtenido == esperado
    estado = "OK  " if ok else "FALLA"
    if not ok:
        _fallos += 1
    print(f"  [{estado}] {descripcion}: obtenido={obtenido!r} esperado={esperado!r}")


def main() -> int:
    # Distribución de prueba P(0..3) para casos simples.
    dist = [0.1, 0.2, 0.3, 0.4]  # suma 1.0

    print("=== GRUPO A (desplazado) ===")
    # "+1" = P(conteo >= 2) = 0.3 + 0.4 = 0.7
    _check('A "+1" = P(>=2)', lineas.probabilidad_linea(lineas.GRUPO_A, "+1", dist), 0.7)
    # "+2" = P(conteo >= 3) = 0.4
    _check('A "+2" = P(>=3)', lineas.probabilidad_linea(lineas.GRUPO_A, "+2", dist), 0.4)

    # "-11" = P(conteo <= 10). Distribución uniforme de 0..11 (12 casilleros).
    dist_larga = [1 / 12] * 12
    _check('A "-11" = P(<=10)', lineas.probabilidad_linea(lineas.GRUPO_A, "-11", dist_larga), 11 / 12)
    # "-4" = P(conteo <= 3) sobre dist corta = 0.1+0.2+0.3+0.4 = 1.0 (todo <=3)
    _check('A "-4" = P(<=3)', lineas.probabilidad_linea(lineas.GRUPO_A, "-4", dist), 1.0)
    # "-2" = P(conteo <= 1) = 0.1 + 0.2 = 0.3
    _check('A "-2" = P(<=1)', lineas.probabilidad_linea(lineas.GRUPO_A, "-2", dist), 0.3)

    print("=== GRUPO B (estándar) ===")
    # "+1" = P(conteo >= 1) = 0.9
    _check('B "+1" = P(>=1)', lineas.probabilidad_linea(lineas.GRUPO_B, "+1", dist), 0.9)
    # "+2" = P(conteo >= 2) = 0.7
    _check('B "+2" = P(>=2)', lineas.probabilidad_linea(lineas.GRUPO_B, "+2", dist), 0.7)

    # Grupo B NO admite lado negativo.
    try:
        lineas.probabilidad_linea(lineas.GRUPO_B, "-2", dist)
        _check("B rechaza línea negativa", "no lanzó error", "ValueError")
    except ValueError:
        _check("B rechaza línea negativa", "ValueError", "ValueError")

    print("=== Generación de etiquetas ===")
    etiquetas_a = lineas.generar_etiquetas(lineas.GRUPO_A, 5)
    tiene_neg_a = any(e.startswith("-") for e in etiquetas_a)
    tiene_pos_a = any(e.startswith("+") for e in etiquetas_a)
    _check("A genera lado positivo", tiene_pos_a, True)
    _check("A genera lado negativo", tiene_neg_a, True)

    etiquetas_b = lineas.generar_etiquetas(lineas.GRUPO_B, 5)
    tiene_neg_b = any(e.startswith("-") for e in etiquetas_b)
    _check("B NO genera líneas negativas", tiene_neg_b, False)
    _check('B genera "+1".."+5"', etiquetas_b, ["+1", "+2", "+3", "+4", "+5"])

    print("=== Mapeo mercado -> grupo ===")
    _check("cards -> A", lineas.grupo_de_mercado("cards"), lineas.GRUPO_A)
    _check("corners -> A", lineas.grupo_de_mercado("corners"), lineas.GRUPO_A)
    _check("goals -> B", lineas.grupo_de_mercado("goals"), lineas.GRUPO_B)

    print()
    if _fallos == 0:
        print("✅ Todos los casos de líneas pasaron.")
        return 0
    print(f"❌ {_fallos} caso(s) fallaron.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

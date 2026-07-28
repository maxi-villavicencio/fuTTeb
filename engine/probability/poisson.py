"""Motor de distribución de Poisson (compartido, reutilizable).

A partir de los goles esperados de un equipo (lambda) calcula la probabilidad
de que marque exactamente 0, 1, 2, ... goles, y con dos lambdas construye la
matriz de probabilidad conjunta de todos los marcadores posibles.

Todo es transparente y auditable (fórmula cerrada de Poisson, sin ML):

    P(X = k) = e^(-λ) · λ^k / k!

Detalle importante para que las probabilidades sumen exactamente 1.0:
el ÚLTIMO casillero de la distribución acumula la cola (P(X >= max_goles)),
en lugar de truncarse. Así la distribución suma 1.0 y la matriz conjunta
suma 1.0 (producto de dos vectores que suman 1.0 cada uno).

Este módulo NO conoce mercados ni base de datos: solo hace probabilidad.
"""

import math


def distribucion(lmbda: float, max_goles: int) -> list[float]:
    """Distribución de Poisson de goles: [P(0), P(1), ..., P(max_goles)].

    El último elemento es P(X >= max_goles) (cola acumulada), de modo que la
    lista suma exactamente 1.0.

    Args:
        lmbda:     goles esperados del equipo (>= 0).
        max_goles: índice máximo de la distribución (p. ej. 8).
    """
    if lmbda < 0:
        raise ValueError(f"lambda no puede ser negativo (recibido: {lmbda}).")
    if max_goles < 1:
        raise ValueError(f"max_goles debe ser >= 1 (recibido: {max_goles}).")

    probs: list[float] = []
    acumulado = 0.0
    for k in range(max_goles):  # 0 .. max_goles-1 exactos
        p = math.exp(-lmbda) * (lmbda ** k) / math.factorial(k)
        probs.append(p)
        acumulado += p

    # Último casillero: toda la cola restante -> garantiza suma 1.0.
    cola = max(0.0, 1.0 - acumulado)
    probs.append(cola)
    return probs


def matriz_conjunta(
    lmbda_local: float,
    lmbda_visitante: float,
    max_goles: int,
) -> list[list[float]]:
    """Matriz de marcadores: matriz[i][j] = P(local=i) · P(visitante=j).

    Asume independencia entre los goles del local y del visitante (supuesto
    estándar del modelo Poisson de fútbol). La matriz suma ~1.0.

    Returns:
        Lista de listas (max_goles+1) x (max_goles+1).
    """
    dist_local = distribucion(lmbda_local, max_goles)
    dist_visitante = distribucion(lmbda_visitante, max_goles)
    return [[pl * pv for pv in dist_visitante] for pl in dist_local]


# --------------------------------------------------------------------------
# Reductores genéricos sobre la matriz (reutilizables por varios mercados)
# --------------------------------------------------------------------------

def suma_matriz(matriz: list[list[float]]) -> float:
    """Suma de todas las probabilidades de la matriz (debe dar ~1.0)."""
    return sum(sum(fila) for fila in matriz)


def prob_total_mayor(matriz: list[list[float]], linea: float) -> float:
    """Probabilidad de que el TOTAL de goles (i+j) supere la línea.

    Con línea 2.5 devuelve P(total >= 3) (Over 2.5).
    """
    total = 0.0
    for i, fila in enumerate(matriz):
        for j, p in enumerate(fila):
            if (i + j) > linea:
                total += p
    return total


def prob_ambos_marcan(matriz: list[list[float]]) -> float:
    """Probabilidad de que ambos equipos marquen al menos 1 (BTTS)."""
    total = 0.0
    for i, fila in enumerate(matriz):
        if i < 1:
            continue
        for j, p in enumerate(fila):
            if j >= 1:
                total += p
    return total


def marcador_mas_probable(matriz: list[list[float]]) -> tuple[tuple[int, int], float]:
    """Devuelve ((goles_local, goles_visitante), probabilidad) del marcador top."""
    mejor_ij = (0, 0)
    mejor_p = -1.0
    for i, fila in enumerate(matriz):
        for j, p in enumerate(fila):
            if p > mejor_p:
                mejor_p = p
                mejor_ij = (i, j)
    return mejor_ij, mejor_p

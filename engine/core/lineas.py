"""Convención de líneas de apuesta (+N / -N) — REGLA DE NEGOCIO compartida.

Traduce una etiqueta de línea ("+2", "-10") a una condición sobre un CONTEO
(tarjetas, córners, goles...) y calcula su probabilidad a partir de una
distribución de probabilidad del conteo (típicamente salida de Poisson).

Esta convención vive SOLO acá; ningún plugin la copia. Hay dos grupos:

──────────────────────────────────────────────────────────────────────────
GRUPO A — numeración DESPLAZADA (mercados: tarjetas, córners)
  - "+N"  significa (N+1) o más.   Ej: +1 = 2 o más ; +2 = 3 o más ; +3 = 4 o más.
  - "-N"  significa (N-1) o menos. Ej: -11 = 10 o menos ; -4 = 3 o menos.
  - Tiene lado POSITIVO y lado NEGATIVO.

GRUPO B — ESTÁNDAR (mercados: goles, remates al arco, faltas cometidas/recibidas)
  - "+N"  significa N o más (equivale a Over (N-0.5)). Ej: +1 = 1 o más ; +2 = 2 o más.
  - NO tiene lado negativo (el piso es 0; no existe línea negativa).
──────────────────────────────────────────────────────────────────────────

Una "distribución" es una lista ``dist`` donde ``dist[k]`` = P(conteo = k) y el
último elemento acumula la cola P(conteo >= max). Debe sumar ~1.0.
"""

# Identificadores de grupo.
GRUPO_A = "A"  # desplazado, con lado negativo (tarjetas, córners)
GRUPO_B = "B"  # estándar, sin lado negativo (goles, remates, faltas)

# Mapa mercado -> grupo. Fuente única para saber qué convención usa cada mercado.
MERCADOS_GRUPO: dict[str, str] = {
    # Grupo A
    "cards": GRUPO_A,
    "corners": GRUPO_A,
    # Grupo B
    "goals": GRUPO_B,
    "shots_on_target": GRUPO_B,
    "fouls_committed": GRUPO_B,
    "fouls_drawn": GRUPO_B,
}


def grupo_de_mercado(mercado: str) -> str:
    """Devuelve el grupo (A/B) de un mercado por su código."""
    try:
        return MERCADOS_GRUPO[mercado]
    except KeyError as exc:
        raise ValueError(
            f"Mercado desconocido para la convención de líneas: {mercado!r}. "
            f"Conocidos: {sorted(MERCADOS_GRUPO)}."
        ) from exc


def _parse_etiqueta(etiqueta: str) -> tuple[int, int]:
    """Parsea '+N'/'-N' -> (signo, N) con signo en {+1, -1} y N entero >= 0."""
    texto = etiqueta.strip()
    if not texto or texto[0] not in "+-":
        raise ValueError(f"Etiqueta de línea inválida: {etiqueta!r} (debe empezar con + o -).")
    signo = 1 if texto[0] == "+" else -1
    try:
        n = int(texto[1:])
    except ValueError as exc:
        raise ValueError(f"Etiqueta de línea inválida: {etiqueta!r}.") from exc
    if n < 0:
        raise ValueError(f"El número de la línea no puede ser negativo: {etiqueta!r}.")
    return signo, n


def _prob_mayor_igual(dist: list[float], k: int) -> float:
    """P(conteo >= k). El último casillero de dist ya acumula la cola."""
    if k <= 0:
        return sum(dist)
    if k >= len(dist):
        return 0.0
    return sum(dist[k:])


def _prob_menor_igual(dist: list[float], k: int) -> float:
    """P(conteo <= k)."""
    if k < 0:
        return 0.0
    if k >= len(dist) - 1:
        return sum(dist)
    return sum(dist[: k + 1])


def probabilidad_linea(grupo: str, etiqueta: str, dist: list[float]) -> float:
    """Probabilidad de que la línea se cumpla, según el grupo y la distribución.

    Grupo A:
        "+N" -> P(conteo >= N+1)
        "-N" -> P(conteo <= N-1)
    Grupo B:
        "+N" -> P(conteo >= N)   (no admite lado negativo)
    """
    signo, n = _parse_etiqueta(etiqueta)

    if grupo == GRUPO_A:
        if signo > 0:
            return _prob_mayor_igual(dist, n + 1)  # +N = (N+1) o más
        return _prob_menor_igual(dist, n - 1)      # -N = (N-1) o menos

    if grupo == GRUPO_B:
        if signo < 0:
            raise ValueError(
                f"El Grupo B (estándar) no tiene lado negativo; línea inválida: {etiqueta!r}."
            )
        return _prob_mayor_igual(dist, n)          # +N = N o más

    raise ValueError(f"Grupo de línea desconocido: {grupo!r} (usar GRUPO_A o GRUPO_B).")


def probabilidad_linea_mercado(mercado: str, etiqueta: str, dist: list[float]) -> float:
    """Igual que probabilidad_linea pero resolviendo el grupo por mercado."""
    return probabilidad_linea(grupo_de_mercado(mercado), etiqueta, dist)


def generar_etiquetas(grupo: str, max_conteo: int) -> list[str]:
    """Genera las etiquetas de línea válidas para un grupo y un conteo máximo.

    Respeta si el grupo tiene lado negativo o no.

    Grupo A (con lado negativo):
        positivas: +1 .. +(max-1)   -> umbrales "2 o más" .. "max o más"
        negativas: -1 .. -max       -> umbrales "0 o menos" .. "(max-1) o menos"
    Grupo B (sin lado negativo):
        positivas: +1 .. +max        -> umbrales "1 o más" .. "max o más"
    """
    if max_conteo < 1:
        raise ValueError("max_conteo debe ser >= 1.")

    if grupo == GRUPO_A:
        positivas = [f"+{n}" for n in range(1, max_conteo)]
        negativas = [f"-{n}" for n in range(1, max_conteo + 1)]
        return positivas + negativas

    if grupo == GRUPO_B:
        return [f"+{n}" for n in range(1, max_conteo + 1)]

    raise ValueError(f"Grupo de línea desconocido: {grupo!r} (usar GRUPO_A o GRUPO_B).")


def descripcion_linea(grupo: str, etiqueta: str) -> str:
    """Texto legible de la línea, p. ej. '+2' (Grupo A) -> '3 o más'."""
    signo, n = _parse_etiqueta(etiqueta)
    if grupo == GRUPO_A:
        if signo > 0:
            return f"{n + 1} o más"
        return f"{n - 1} o menos"
    if grupo == GRUPO_B:
        if signo < 0:
            raise ValueError(f"El Grupo B no tiene lado negativo: {etiqueta!r}.")
        return f"{n} o más"
    raise ValueError(f"Grupo de línea desconocido: {grupo!r}.")

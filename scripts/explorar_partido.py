"""Script de EXPLORACIÓN de la API-Football (NO toca la base de datos).

Objetivo: traer UN partido ya jugado de la Liga Profesional Argentina y mostrar
por consola sus datos crudos y estadísticas, para ENTENDER la estructura de la
respuesta antes de diseñar la carga a la base (próximo sprint).

Cuidado con el quota (plan gratuito = 100 requests/día): este script hace como
máximo 3 requests:
    1) /fixtures            -> lista de partidos finalizados (una sola llamada)
    2) /fixtures/statistics -> estadísticas del partido elegido
    3) /fixtures/lineups    -> alineaciones del partido elegido (opcional)

Ejecutar desde la raíz del proyecto:

    python scripts/explorar_partido.py

La API key se lee del .env (variable API_FOOTBALL_KEY); NUNCA se hardcodea.
"""

import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

# --- Configuración --------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

BASE_URL = "https://v3.football.api-sports.io"
LEAGUE_ID = 128     # Liga Profesional Argentina
NOMBRE_HEADER_KEY = "x-apisports-key"

# Temporada a explorar. OJO: el plan GRATUITO de API-Football solo da acceso a
# las temporadas 2022 a 2024. La temporada objetivo del proyecto (2026) requiere
# un plan de pago. Como este script solo busca ENTENDER la estructura de la
# respuesta (idéntica en cualquier temporada), usamos 2024 por defecto.
# Se puede sobreescribir con la variable de entorno API_FOOTBALL_SEASON.
SEASON = int(os.getenv("API_FOOTBALL_SEASON", "2024"))

# Contador global de requests para controlar el quota.
_requests_hechos = 0


def _abortar(mensaje: str) -> None:
    """Imprime un error en español y corta la ejecución."""
    print(f"\n❌ {mensaje}")
    print(f"   Requests hechos hasta el corte: {_requests_hechos}")
    sys.exit(1)


def hacer_request(path: str, params: dict, api_key: str) -> dict:
    """Hace un GET a la API-Football manejando errores comunes en español.

    Devuelve el JSON completo de la respuesta. Corta la ejecución ante errores
    graves (key inválida, quota agotado, sin conexión).
    """
    global _requests_hechos
    url = f"{BASE_URL}{path}"
    headers = {NOMBRE_HEADER_KEY: api_key}

    try:
        _requests_hechos += 1
        resp = requests.get(url, headers=headers, params=params, timeout=20)
    except requests.exceptions.RequestException as exc:
        _abortar(f"No se pudo conectar con la API-Football: {exc}")

    # 429 = se acabó el quota / demasiadas llamadas.
    if resp.status_code == 429:
        _abortar(
            "Se agotó el quota de la API (error 429). El plan gratuito permite "
            "100 requests por día. Probá de nuevo mañana."
        )
    if resp.status_code in (401, 403):
        _abortar("La API rechazó la autenticación (¿API key inválida o vencida?).")
    if resp.status_code != 200:
        _abortar(f"La API respondió con código {resp.status_code}: {resp.text[:200]}")

    datos = resp.json()

    # La API-Football devuelve 200 con un campo "errors" aunque haya problemas.
    errores = datos.get("errors")
    if errores:
        # Puede venir como dict {"token": "..."} o como lista.
        if isinstance(errores, dict) and errores:
            detalle = "; ".join(f"{k}: {v}" for k, v in errores.items())
            if "token" in errores or "key" in errores:
                _abortar(f"Problema con la API key: {detalle}")
            if "requests" in errores:
                _abortar(f"Límite de requests alcanzado: {detalle}")
            _abortar(f"La API devolvió errores: {detalle}")
        if isinstance(errores, list) and len(errores) > 0:
            _abortar(f"La API devolvió errores: {errores}")

    return datos


def separador(titulo: str) -> None:
    print("\n" + "=" * 70)
    print(f" {titulo}")
    print("=" * 70)


def main() -> int:
    api_key = os.getenv("API_FOOTBALL_KEY", "").strip()
    if not api_key:
        _abortar(
            "No se encontró la API key. Definí API_FOOTBALL_KEY en el archivo .env "
            "de la raíz del proyecto."
        )

    print("Explorando API-Football (modo SOLO LECTURA, no toca la base).")
    print(f"Liga: {LEAGUE_ID} (Liga Profesional Argentina) | Temporada: {SEASON}")

    # --- 1) Partidos finalizados (una sola llamada) -----------------------
    separador("1) Buscando partidos finalizados (status FT)")
    fixtures = hacer_request(
        "/fixtures",
        {"league": LEAGUE_ID, "season": SEASON, "status": "FT"},
        api_key,
    )
    partidos = fixtures.get("response", [])
    print(f"Partidos finalizados encontrados: {len(partidos)}")

    if not partidos:
        _abortar(
            "No hay partidos finalizados para esa liga/temporada. Probá con otra "
            "temporada (season) o verificá que la liga tenga partidos jugados."
        )

    # Elegir el MÁS RECIENTE jugado (ordenar por fecha del fixture, descendente).
    partidos.sort(key=lambda p: p["fixture"]["date"], reverse=True)
    partido = partidos[0]

    fx = partido["fixture"]
    equipos = partido["teams"]
    goles = partido["goals"]
    fixture_id = fx["id"]

    # --- Datos crudos del partido -----------------------------------------
    separador("2) Datos del partido elegido (el más reciente)")
    print(f"Fixture id : {fixture_id}")
    print(f"Fecha      : {fx.get('date')}")
    print(f"Estado     : {fx.get('status', {}).get('long')} "
          f"({fx.get('status', {}).get('short')})")
    venue = fx.get("venue", {}) or {}
    print(f"Estadio    : {venue.get('name')} ({venue.get('city')})")
    print(f"Árbitro    : {fx.get('referee')}")
    print(f"Local      : {equipos['home']['name']} (id {equipos['home']['id']})")
    print(f"Visitante  : {equipos['away']['name']} (id {equipos['away']['id']})")
    print(f"Resultado  : {goles.get('home')} - {goles.get('away')}")

    # --- 3) Estadísticas del partido --------------------------------------
    separador("3) Estadísticas por equipo (nombres EXACTOS de la API)")
    stats_resp = hacer_request(
        "/fixtures/statistics", {"fixture": fixture_id}, api_key
    )
    equipos_stats = stats_resp.get("response", [])

    campos_detectados: list[str] = []  # para el resumen final

    if not equipos_stats:
        print("⚠ Este partido no trae estadísticas cargadas en la API.")
    else:
        for bloque in equipos_stats:
            nombre_equipo = bloque.get("team", {}).get("name", "¿?")
            print(f"\n--- {nombre_equipo} ---")
            for stat in bloque.get("statistics", []):
                tipo = stat.get("type")      # nombre EXACTO del campo
                valor = stat.get("value")    # puede ser int, str ("55%") o None
                print(f"  {tipo!r:<24} = {valor!r}  (tipo Python: {type(valor).__name__})")
            # Guardar los nombres de campos del primer equipo (ambos comparten set).
            if not campos_detectados:
                campos_detectados = [
                    s.get("type") for s in bloque.get("statistics", [])
                ]

    # --- 4) Alineaciones (opcional, si el quota lo permite) ---------------
    separador("4) Alineaciones (opcional)")
    lineups_resp = hacer_request(
        "/fixtures/lineups", {"fixture": fixture_id}, api_key
    )
    lineups = lineups_resp.get("response", [])
    if not lineups:
        print("⚠ Este partido no trae alineaciones cargadas en la API.")
    else:
        for bloque in lineups:
            nombre_equipo = bloque.get("team", {}).get("name", "¿?")
            formacion = bloque.get("formation")
            print(f"\n--- {nombre_equipo} | formación: {formacion} ---")
            for titular in bloque.get("startXI", []):
                jug = titular.get("player", {})
                print(f"  #{jug.get('number')} {jug.get('name')} ({jug.get('pos')})")

    # --- 5) Resumen de campos para el mapeo a MatchStatistics -------------
    separador("5) RESUMEN: campos de estadísticas que devuelve la API")
    if campos_detectados:
        print("Estos son los nombres EXACTOS a mapear a columnas de MatchStatistics:")
        for i, campo in enumerate(campos_detectados, 1):
            print(f"  {i:>2}. {campo!r}")
    else:
        print("No se detectaron campos de estadísticas en este partido.")

    # --- Control de quota -------------------------------------------------
    separador("Control de quota")
    print(f"Total de requests hechos en esta corrida: {_requests_hechos}")
    print("(Plan gratuito: 100 requests por día.)")

    return 0


if __name__ == "__main__":
    sys.exit(main())

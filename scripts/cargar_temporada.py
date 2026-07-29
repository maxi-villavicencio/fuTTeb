"""Cargador REANUDABLE de una temporada desde API-Football a BetAnalyzerAI.

Carga las estadísticas reales de los partidos finalizados de la Liga Profesional
Argentina (o la liga indicada), temporada por temporada. Está pensado para
correrse VARIOS DÍAS seguidos respetando el límite de 100 requests/día del plan
gratuito: es idempotente (no duplica) y reanudable (retoma donde quedó).

Uso (desde la raíz del proyecto):

    python scripts/cargar_temporada.py            # temporada por defecto (2024)
    python scripts/cargar_temporada.py 2023       # otra temporada

Configuración por entorno (.env):
    API_FOOTBALL_KEY              (obligatoria)  key de API-Football.
    API_FOOTBALL_LIMITE_REQUESTS (opcional, 90) frenar antes de gastar el quota.
    API_FOOTBALL_PAUSA           (opcional, 6.0) segundos de pausa entre requests
                                                 (evita el límite por minuto).

NO guarda alineaciones (solo estadísticas). NO hardcodea la key.

Nota de plan gratuito: solo hay acceso a temporadas 2022-2024. Para 2026 (la
temporada objetivo del proyecto) hace falta un plan de pago; el código no cambia.
"""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from sqlalchemy import text

# --- Configuración --------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from backend.app.database import get_engine  # noqa: E402

BASE_URL = "https://v3.football.api-sports.io"
NOMBRE_HEADER_KEY = "x-apisports-key"
LEAGUE_ID = 128  # Liga Profesional Argentina

# Frenar antes de agotar el quota diario (100). Por defecto paramos en 90.
LIMITE_REQUESTS = int(os.getenv("API_FOOTBALL_LIMITE_REQUESTS", "90"))
# Pausa entre requests para no chocar con el límite por minuto del plan.
PAUSA_SEGUNDOS = float(os.getenv("API_FOOTBALL_PAUSA", "6.0"))

# Mapeo de estadísticas de la API -> columnas tipadas de MatchStatistics.
#   clave = nombre EXACTO de la API ; valor = (columna, tipo)
CAMPOS_COLUMNA = {
    "Corner Kicks": ("corners", "int"),
    "Yellow Cards": ("yellow_cards", "int"),
    "Red Cards": ("red_cards", "int"),          # None -> 0
    "Total Shots": ("shots", "int"),
    "Shots on Goal": ("shots_on_target", "int"),
    "Ball Possession": ("possession", "pct"),   # "47%" -> 47.0
    "Fouls": ("fouls", "int"),
    "Offsides": ("offsides", "int"),
    "expected_goals": ("expected_goals", "dec"),  # "0.91" -> 0.91 (None -> NULL)
}

# Campos que van a MatchStatisticExtras (clave-valor). clave = nombre API.
#   valor = metric_key con el que se guardan.
CAMPOS_EXTRA = {
    "Shots off Goal": "shots_off_goal",
    "Blocked Shots": "blocked_shots",
    "Shots insidebox": "shots_insidebox",
    "Shots outsidebox": "shots_outsidebox",
    "Total passes": "total_passes",
    "Passes accurate": "passes_accurate",
    "Passes %": "passes_pct",
    "Goalkeeper Saves": "goalkeeper_saves",
    "goals_prevented": "goals_prevented",
}


# --- Errores propios ------------------------------------------------------
class QuotaAgotada(Exception):
    """Se agotó (o casi) el quota diario / se alcanzó el límite de requests."""


# --- Estado de la corrida -------------------------------------------------
_requests_hechos = 0


# --- Utilidades de limpieza (datos crudos -> valores limpios) -------------
def a_entero(valor) -> int:
    """None -> 0 ; '5' -> 5. Para conteos (córners, tarjetas, tiros...)."""
    if valor is None:
        return 0
    try:
        return int(valor)
    except (TypeError, ValueError):
        try:
            return int(float(str(valor).replace("%", "").strip()))
        except (TypeError, ValueError):
            return 0


def a_decimal(valor):
    """'0.91' -> 0.91 ; '47%' -> 47.0 ; None -> None. Para xG, posesión, etc."""
    if valor is None:
        return None
    try:
        return float(str(valor).replace("%", "").strip())
    except (TypeError, ValueError):
        return None


# --- Cliente HTTP ---------------------------------------------------------
def hacer_request(path: str, params: dict, api_key: str) -> dict:
    """GET a la API-Football. Cuenta el request y maneja errores.

    Lanza QuotaAgotada si se alcanza el límite (429 o error de quota diaria).
    Deja propagar requests.RequestException para que el llamador decida.
    """
    global _requests_hechos
    _requests_hechos += 1
    resp = requests.get(
        f"{BASE_URL}{path}",
        headers={NOMBRE_HEADER_KEY: api_key},
        params=params,
        timeout=20,
    )

    if resp.status_code == 429:
        raise QuotaAgotada("La API respondió 429 (demasiadas requests).")
    if resp.status_code in (401, 403):
        raise RuntimeError("Autenticación rechazada (¿API key inválida o vencida?).")
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

    datos = resp.json()
    errores = datos.get("errors")
    if errores:
        if isinstance(errores, dict):
            texto = "; ".join(f"{k}: {v}" for k, v in errores.items())
            if "requests" in errores or "rateLimit" in errores:
                raise QuotaAgotada(f"Límite de requests alcanzado: {texto}")
            raise RuntimeError(f"La API devolvió errores: {texto}")
        if isinstance(errores, list) and errores:
            raise RuntimeError(f"La API devolvió errores: {errores}")

    return datos


# --- Upserts (idempotentes por external_ref) ------------------------------
def _get_or_create(conn, tabla: str, external_ref: str, insert_sql: str, params: dict):
    """Devuelve el id existente por external_ref, o inserta y devuelve el nuevo."""
    fila = conn.execute(
        text(f"SELECT id FROM dbo.{tabla} WHERE external_ref = :e"),
        {"e": external_ref},
    ).first()
    if fila:
        return int(fila.id)
    return int(conn.execute(text(insert_sql), params).scalar())


def _upsert_competicion(conn, league_id: int) -> int:
    ext = f"APIF-LEAGUE-{league_id}"
    return _get_or_create(
        conn, "Competitions", ext,
        "INSERT INTO dbo.Competitions (name, country, type, external_ref) "
        "OUTPUT INSERTED.id VALUES (:n, :c, :t, :e)",
        {"n": "Liga Profesional Argentina", "c": "Argentina", "t": "liga", "e": ext},
    )


def _upsert_temporada(conn, competition_id: int, league_id: int, season: int) -> int:
    ext = f"APIF-SEASON-{league_id}-{season}"
    return _get_or_create(
        conn, "Seasons", ext,
        "INSERT INTO dbo.Seasons (competition_id, name, is_current, external_ref) "
        "OUTPUT INSERTED.id VALUES (:cid, :n, 0, :e)",
        {"cid": competition_id, "n": str(season), "e": ext},
    )


def _upsert_equipo(conn, api_team: dict) -> int:
    ext = f"APIF-TEAM-{api_team['id']}"
    nombre = api_team.get("name") or f"Equipo {api_team['id']}"
    return _get_or_create(
        conn, "Teams", ext,
        "INSERT INTO dbo.Teams (name, short_name, country, external_ref) "
        "OUTPUT INSERTED.id VALUES (:n, :s, :c, :e)",
        {"n": nombre, "s": nombre[:50], "c": "Argentina", "e": ext},
    )


def _upsert_arbitro(conn, nombre):
    if not nombre:
        return None
    ext = f"APIF-REF-{nombre}"[:100]
    return _get_or_create(
        conn, "Referees", ext,
        "INSERT INTO dbo.Referees (name, external_ref) OUTPUT INSERTED.id VALUES (:n, :e)",
        {"n": nombre[:150], "e": ext},
    )


def _upsert_estadio(conn, venue):
    if not venue or not venue.get("name"):
        return None
    vid = venue.get("id")
    ext = (f"APIF-VENUE-{vid}" if vid else f"APIF-VENUE-{venue['name']}")[:100]
    return _get_or_create(
        conn, "Venues", ext,
        "INSERT INTO dbo.Venues (name, city, external_ref) OUTPUT INSERTED.id "
        "VALUES (:n, :c, :e)",
        {"n": venue["name"][:150], "c": (venue.get("city") or None), "e": ext},
    )


def _parsear_fecha(iso_str):
    """'2024-12-17T00:00:00+00:00' -> datetime naive en UTC (para datetime2)."""
    if not iso_str:
        return None
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _insertar_fila_stats(conn, match_id, team_id, opp_id, is_home, goles, goles_rival, stats):
    """Inserta una fila en MatchStatistics y devuelve su id (para los extras)."""
    columnas = {
        "match_id": match_id,
        "team_id": team_id,
        "opponent_team_id": opp_id,
        "is_home": 1 if is_home else 0,
        "goals": goles,
        "goals_conceded": goles_rival,
        # valores por defecto (se completan abajo según el mapeo)
        "corners": 0, "yellow_cards": 0, "red_cards": 0, "shots": 0,
        "shots_on_target": 0, "possession": None, "fouls": 0,
        "offsides": 0, "expected_goals": None,
    }
    for campo_api, (columna, tipo) in CAMPOS_COLUMNA.items():
        crudo = stats.get(campo_api)
        if tipo == "int":
            columnas[columna] = a_entero(crudo)
        else:  # "pct" o "dec"
            columnas[columna] = a_decimal(crudo)

    sql = text(
        "INSERT INTO dbo.MatchStatistics "
        "(match_id, team_id, opponent_team_id, is_home, goals, goals_conceded, "
        " corners, yellow_cards, red_cards, shots, shots_on_target, possession, "
        " fouls, offsides, expected_goals) "
        "OUTPUT INSERTED.id "
        "VALUES (:match_id, :team_id, :opponent_team_id, :is_home, :goals, "
        " :goals_conceded, :corners, :yellow_cards, :red_cards, :shots, "
        " :shots_on_target, :possession, :fouls, :offsides, :expected_goals)"
    )
    stat_id = int(conn.execute(sql, columnas).scalar())

    # Extras (clave-valor): solo los que tengan valor.
    for campo_api, metric_key in CAMPOS_EXTRA.items():
        valor = a_decimal(stats.get(campo_api))
        if valor is None:
            continue
        conn.execute(
            text(
                "INSERT INTO dbo.MatchStatisticExtras (match_stat_id, metric_key, metric_value) "
                "VALUES (:sid, :k, :v)"
            ),
            {"sid": stat_id, "k": metric_key, "v": valor},
        )
    return stat_id


# --- Carga de un partido (una transacción atómica) ------------------------
def cargar_partido(engine, fixture, competition_id, season_id, stats_por_equipo) -> str:
    """Inserta un partido y sus estadísticas en una sola transacción.

    Devuelve "con_stats" o "sin_stats". Si algo falla, la transacción se
    revierte entera (el partido queda sin cargar y se reintenta en otra corrida).
    """
    fx = fixture["fixture"]
    equipos = fixture["teams"]
    goles = fixture["goals"]
    fixture_id = fx["id"]

    with engine.begin() as conn:
        home_id = _upsert_equipo(conn, equipos["home"])
        away_id = _upsert_equipo(conn, equipos["away"])
        referee_id = _upsert_arbitro(conn, fx.get("referee"))
        venue_id = _upsert_estadio(conn, fx.get("venue"))

        match_id = int(
            conn.execute(
                text(
                    "INSERT INTO dbo.Matches "
                    "(competition_id, season_id, kickoff_at, home_team_id, away_team_id, "
                    " referee_id, venue_id, status, external_ref) "
                    "OUTPUT INSERTED.id "
                    "VALUES (:cid, :sid, :ko, :h, :a, :ref, :ven, :st, :ext)"
                ),
                {
                    "cid": competition_id, "sid": season_id,
                    "ko": _parsear_fecha(fx.get("date")),
                    "h": home_id, "a": away_id,
                    "ref": referee_id, "ven": venue_id,
                    "st": (fx.get("status", {}) or {}).get("short", "FT"),
                    "ext": str(fixture_id),
                },
            ).scalar()
        )

        stats_home = stats_por_equipo.get(equipos["home"]["id"])
        stats_away = stats_por_equipo.get(equipos["away"]["id"])

        # Si no hay estadísticas, se inserta igual el partido (para no re-pedirlo)
        # pero sin filas de MatchStatistics.
        if stats_home is None and stats_away is None:
            return "sin_stats"

        _insertar_fila_stats(
            conn, match_id, home_id, away_id, True,
            goles.get("home"), goles.get("away"), stats_home or {},
        )
        _insertar_fila_stats(
            conn, match_id, away_id, home_id, False,
            goles.get("away"), goles.get("home"), stats_away or {},
        )
        return "con_stats"


def _fixture_ya_cargado(engine, fixture_id: int) -> bool:
    with engine.connect() as conn:
        fila = conn.execute(
            text("SELECT 1 FROM dbo.Matches WHERE external_ref = :e"),
            {"e": str(fixture_id)},
        ).first()
    return fila is not None


# --- Programa principal ---------------------------------------------------
def main() -> int:
    api_key = os.getenv("API_FOOTBALL_KEY", "").strip()
    if not api_key:
        print("❌ No se encontró API_FOOTBALL_KEY en el .env.")
        return 1

    season = int(sys.argv[1]) if len(sys.argv) > 1 else int(
        os.getenv("API_FOOTBALL_SEASON", "2024")
    )
    engine = get_engine()

    print("Cargador de temporada (API-Football -> BetAnalyzerAI)")
    print(f"Liga: {LEAGUE_ID} | Temporada: {season}")
    print(f"Límite de requests de esta corrida: {LIMITE_REQUESTS} (quota diario: 100)")
    print("-" * 66)

    # 1) Lista de fixtures finalizados (1 request).
    try:
        fixtures_resp = hacer_request(
            "/fixtures",
            {"league": LEAGUE_ID, "season": season, "status": "FT"},
            api_key,
        )
    except QuotaAgotada as exc:
        print(f"❌ {exc}\n   No se pudo ni traer la lista de partidos. Probá más tarde.")
        return 1
    except Exception as exc:
        print(f"❌ No se pudo traer la lista de partidos: {exc}")
        return 1

    fixtures = fixtures_resp.get("response", [])
    total = len(fixtures)
    print(f"Partidos finalizados en la temporada: {total}")
    if total == 0:
        print("⚠ No hay partidos finalizados (¿temporada sin datos o sin acceso?).")
        return 0

    # Cargar los más antiguos primero (orden cronológico) para un avance natural.
    fixtures.sort(key=lambda p: p["fixture"]["date"])

    # Competición y temporada: se resuelven UNA sola vez (no gasta requests).
    with engine.begin() as conn:
        competition_id = _upsert_competicion(conn, LEAGUE_ID)
        season_id = _upsert_temporada(conn, competition_id, LEAGUE_ID, season)

    existentes = nuevos = sin_stats = fallidos = 0
    detenido_por_quota = False

    for fixture in fixtures:
        fixture_id = fixture["fixture"]["id"]

        # 3) Idempotencia: si ya está, se saltea SIN gastar request.
        if _fixture_ya_cargado(engine, fixture_id):
            existentes += 1
            continue

        # 5) Control de quota: frenar ANTES de pasarnos.
        if _requests_hechos >= LIMITE_REQUESTS:
            detenido_por_quota = True
            break

        # 4) Pedir estadísticas del partido y cargarlo.
        try:
            if PAUSA_SEGUNDOS > 0:
                time.sleep(PAUSA_SEGUNDOS)
            stats_resp = hacer_request(
                "/fixtures/statistics", {"fixture": fixture_id}, api_key
            )
        except QuotaAgotada as exc:
            print(f"\n⏸  {exc}")
            detenido_por_quota = True
            break
        except requests.exceptions.RequestException as exc:
            print(f"  ⚠ Partido {fixture_id}: error de red ({exc}). Se continúa.")
            fallidos += 1
            continue
        except Exception as exc:
            print(f"  ⚠ Partido {fixture_id}: {exc}. Se continúa.")
            fallidos += 1
            continue

        stats_por_equipo = {
            b["team"]["id"]: {s["type"]: s["value"] for s in b.get("statistics", [])}
            for b in stats_resp.get("response", [])
        }

        # Guardar el partido (transacción atómica). Si falla, se revierte ese
        # partido y se continúa con el siguiente (se reintenta en otra corrida).
        try:
            resultado = cargar_partido(
                engine, fixture, competition_id, season_id, stats_por_equipo
            )
        except Exception as exc:
            print(f"  ⚠ Partido {fixture_id}: error al guardar ({exc}). Se continúa.")
            fallidos += 1
            continue

        eq = fixture["teams"]
        g = fixture["goals"]
        marca = "sin stats" if resultado == "sin_stats" else "OK"
        if resultado == "sin_stats":
            sin_stats += 1
        else:
            nuevos += 1
        print(
            f"  [{marca}] {eq['home']['name']} {g.get('home')}-{g.get('away')} "
            f"{eq['away']['name']}  (fixture {fixture_id})"
        )

    # --- Resumen de la corrida --------------------------------------------
    cargados_ahora = nuevos + sin_stats
    faltan = total - existentes - cargados_ahora

    print("\n" + "=" * 66)
    print(" RESUMEN DE LA CORRIDA")
    print("=" * 66)
    print(f"  Temporada                     : {season}")
    print(f"  Partidos en la temporada      : {total}")
    print(f"  Ya existentes (saltados)      : {existentes}")
    print(f"  Nuevos cargados con stats     : {nuevos}")
    print(f"  Nuevos cargados SIN stats     : {sin_stats}")
    print(f"  Fallidos (se reintentan)      : {fallidos}")
    print(f"  Requests usados en esta corrida: {_requests_hechos} (límite {LIMITE_REQUESTS})")
    print(f"  Faltan para completar         : {faltan}")

    if detenido_por_quota:
        print("\n⏸  Límite diario casi alcanzado. Cargados "
              f"{cargados_ahora} partidos nuevos en esta corrida.")
        print("   Volvé a correr mañana para continuar (retoma donde quedó).")
    elif faltan <= 0:
        print("\n✅ Temporada COMPLETA. No faltan partidos por cargar.")
    else:
        print(f"\nℹ Corrida terminada. Volvé a correr para cargar los {faltan} restantes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

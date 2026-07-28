"""Prueba de conexión Python -> pyodbc -> SQL Server -> BetAnalyzerAI.

Objetivo mínimo: confirmar que toda la cadena funciona leyendo datos REALES
de la tabla Markets (los 4 mercados sembrados).

Ejecutar desde la raíz del proyecto:

    python backend/test_connection.py

Toda la configuración (servidor, base, credenciales, driver) sale del archivo
.env de la raíz; aquí no hay nada hardcodeado.
"""

import sys
from pathlib import Path

# Permitir "python backend/test_connection.py" desde la raíz del proyecto:
# agregamos la raíz al sys.path para poder importar el paquete backend.app.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402

from backend.app.config import settings  # noqa: E402
from backend.app.database import get_engine  # noqa: E402


def probar_conexion() -> int:
    """Se conecta, consulta la tabla Markets e imprime las filas.

    Devuelve un código de salida (0 = éxito, 1 = error) para poder usarlo en
    scripts/CI.
    """
    print("=" * 60)
    print(" Prueba de conexión a SQL Server — BetAnalyzerAI")
    print("=" * 60)
    print(f" Servidor : {settings.DB_SERVER or '(vacío)'}")
    print(f" Base     : {settings.DB_NAME or '(vacío)'}")
    print(f" Driver   : {settings.DB_DRIVER}")
    print(f" Usuario  : {settings.DB_USER or '(vacío)'}")
    print("-" * 60)

    try:
        engine = get_engine()

        with engine.connect() as conn:
            resultado = conn.execute(
                text("SELECT id, code, name FROM dbo.Markets ORDER BY id")
            )
            filas = resultado.fetchall()

        if not filas:
            print("⚠️  Conexión OK, pero la tabla Markets está vacía.")
            print("    Revisá que hayas ejecutado database/04_seed_markets.sql.")
            return 1

        print(f"✅ Conexión exitosa. Mercados encontrados: {len(filas)}\n")
        print(f"  {'id':>3} | {'code':<10} | nombre")
        print(f"  {'-' * 3} | {'-' * 10} | {'-' * 30}")
        for fila in filas:
            print(f"  {fila.id:>3} | {fila.code:<10} | {fila.name}")
        print("\n🎉 La cadena Python -> pyodbc -> SQL Server funciona.")
        return 0

    except SQLAlchemyError as exc:
        print("❌ ERROR: no se pudo conectar o consultar la base de datos.\n")
        print(f"Detalle técnico:\n{exc}\n")
        _imprimir_ayuda()
        return 1
    except Exception as exc:  # pragma: no cover - red de seguridad
        print(f"❌ ERROR inesperado: {exc}\n")
        _imprimir_ayuda()
        return 1


def _imprimir_ayuda() -> None:
    """Imprime una guía de qué revisar si la conexión falla."""
    print("Qué revisar si falla:")
    print("  1. ¿Existe el archivo .env en la raíz con DB_SERVER, DB_NAME,")
    print("     DB_USER, DB_PASSWORD y DB_DRIVER?")
    print("  2. ¿El servidor es correcto? Instancia nombrada: MAXI\\SQLEXPRESS")
    print("  3. ¿Está instalado el 'ODBC Driver 18 for SQL Server'?")
    print("  4. Driver 18 exige cifrado: la cadena usa TrustServerCertificate=yes")
    print("     y Encrypt=optional. Si cambiaste el .env, verificá esos valores.")
    print("  5. ¿El servicio SQL Server (SQLEXPRESS) está iniciado?")
    print("  6. ¿El login/usuario y la contraseña son correctos y tienen acceso")
    print("     a la base BetAnalyzerAI?")


if __name__ == "__main__":
    sys.exit(probar_conexion())

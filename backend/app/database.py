"""Conexión del backend a SQL Server (SQLAlchemy + pyodbc).

Deja lista la infraestructura de conexión mediante el dialecto
``mssql+pyodbc``, SIN definir modelos ni tablas. La cadena se construye a
partir de las variables de entorno cargadas en ``config.settings``.

En esta fase el engine de SQLAlchemy se crea de forma perezosa para que la
app pueda arrancar (y responder ``/health``) aunque todavía no exista una
base de datos configurada.
"""

from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# Base declarativa para futuros modelos (aún sin tablas).
Base = declarative_base()

# El Engine y la fábrica de sesiones se inicializan bajo demanda.
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def build_connection_url() -> str:
    """Construye la URL de conexión ``mssql+pyodbc`` desde el entorno.

    Prioriza ``DATABASE_URL`` si está definida; en caso contrario compone la
    cadena a partir de los componentes individuales.
    """
    if settings.DATABASE_URL:
        return settings.DATABASE_URL

    # Nota Driver 18: exige cifrado por defecto. En local sin certificado válido
    # hace falta TrustServerCertificate=yes (y Encrypt=optional) o la conexión
    # falla con un error de SSL/certificado.
    odbc_params = quote_plus(
        f"DRIVER={{{settings.DB_DRIVER}}};"
        f"SERVER={settings.DB_SERVER};"  # soporta instancia nombrada: MAXI\\SQLEXPRESS
        f"DATABASE={settings.DB_NAME};"
        f"UID={settings.DB_USER};"
        f"PWD={settings.DB_PASSWORD};"
        f"Encrypt={settings.DB_ENCRYPT};"
        f"TrustServerCertificate={settings.DB_TRUST_SERVER_CERTIFICATE}"
    )
    return f"mssql+pyodbc:///?odbc_connect={odbc_params}"


def get_engine() -> Engine:
    """Devuelve el Engine de SQLAlchemy, creándolo la primera vez."""
    global _engine
    if _engine is None:
        _engine = create_engine(build_connection_url(), pool_pre_ping=True)
    return _engine


def get_session():
    """Dependencia de FastAPI: entrega una sesión y la cierra al final."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(), autocommit=False, autoflush=False
        )
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()

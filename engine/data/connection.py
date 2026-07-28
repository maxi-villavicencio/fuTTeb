"""Conexión del engine a SQL Server.

Reutiliza la configuración de conexión ya existente en el backend
(``backend.app.database``), que lee las credenciales del ``.env`` de la raíz.
Importante: ese módulo NO importa FastAPI (solo SQLAlchemy + dotenv), así que
el engine sigue siendo independiente de la capa web.

Se centraliza aquí el acceso al ``Engine`` de SQLAlchemy para que los
repositorios de ``engine.data`` no dependan de rutas concretas del backend.
"""

from sqlalchemy.engine import Engine

from backend.app.database import get_engine as _get_backend_engine


def get_engine() -> Engine:
    """Devuelve el Engine de SQLAlchemy compartido (conexión a SQL Server)."""
    return _get_backend_engine()

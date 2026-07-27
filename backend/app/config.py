"""Configuración del backend.

Carga la configuración desde variables de entorno (incluida la cadena de
conexión a SQL Server). Sin credenciales hardcodeadas: ver ``.env.example``.
"""

import os


class Settings:
    """Configuración mínima leída de variables de entorno.

    En esta fase de scaffolding solo se exponen los valores necesarios para
    construir la cadena de conexión a SQL Server. Más adelante puede migrarse
    a ``pydantic-settings`` si se desea validación estricta.
    """

    # Componentes de la conexión a SQL Server (todos por entorno).
    DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_SERVER: str = os.getenv("DB_SERVER", "")
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # Alternativa: cadena de conexión completa ya formada.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    APP_NAME: str = os.getenv("APP_NAME", "Bet Analyzer AI")


settings = Settings()

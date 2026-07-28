"""Configuración del backend.

Carga la configuración desde el archivo ``.env`` de la raíz del proyecto
(usando python-dotenv) y expone los valores necesarios para construir la
cadena de conexión a SQL Server. Sin credenciales hardcodeadas: ver
``.env.example``.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Raíz del proyecto: backend/app/config.py -> subir 3 niveles hasta la raíz.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Cargar el .env de la raíz (si existe). No sobrescribe variables ya definidas
# en el entorno del sistema.
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Configuración mínima leída de variables de entorno.

    En esta fase solo se exponen los valores necesarios para construir la
    cadena de conexión a SQL Server. Más adelante puede migrarse a
    ``pydantic-settings`` si se desea validación estricta.
    """

    # Componentes de la conexión a SQL Server (todos por entorno, nunca hardcodeados).
    DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    DB_SERVER: str = os.getenv("DB_SERVER", "")  # p. ej. MAXI\SQLEXPRESS
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # Cifrado del Driver 18: en local sin certificado hace falta confiar en el
    # certificado del servidor para que la conexión no falle.
    DB_TRUST_SERVER_CERTIFICATE: str = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")
    DB_ENCRYPT: str = os.getenv("DB_ENCRYPT", "optional")

    # Alternativa: cadena de conexión completa ya formada.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    APP_NAME: str = os.getenv("APP_NAME", "Bet Analyzer AI")

    # Orígenes permitidos para CORS (el frontend en desarrollo).
    # Lista separada por comas en la variable de entorno CORS_ORIGINS.
    CORS_ORIGINS: list[str] = [
        origen.strip()
        for origen in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if origen.strip()
    ]


settings = Settings()

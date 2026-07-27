"""Capa de datos del engine.

Repositorios que LEEN datos históricos y de contexto desde SQL Server para
alimentar a los mercados. El engine no conoce FastAPI: gestiona su propia
conexión a la base de datos de forma independiente.

    connection.py    -> creación del engine/conexión de SQLAlchemy a SQL Server
    repositories.py  -> repositorios de lectura (partidos, estadísticas, ...)
"""
